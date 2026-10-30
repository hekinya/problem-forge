-- Build a contest booklet by converting each problem Markdown independently.

local script_directory = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local problem_filter = dofile(pandoc.path.join({script_directory, "polygon.lua"}))

local function metadata_text(value)
  if value == nil then
    return nil
  end
  return pandoc.utils.stringify(value)
end

local function required_text(value, description)
  local result = metadata_text(value)
  if result == nil or result == "" then
    error("missing " .. description, 0)
  end
  return result
end

local function read_file(path)
  local file, message = io.open(path, "rb")
  if not file then
    error("cannot read '" .. path .. "': " .. message, 0)
  end
  local contents = file:read("*a")
  file:close()
  return contents
end

local function write_file(path, contents)
  local file, message = io.open(path, "wb")
  if not file then
    error("cannot write '" .. path .. "': " .. message, 0)
  end
  file:write(contents)
  file:close()
end

local function alphabetical_index(number)
  local result = ""
  while number > 0 do
    local remainder = (number - 1) % 26
    result = string.char(string.byte("A") + remainder) .. result
    number = math.floor((number - 1) / 26)
  end
  return result
end

local function normalize_language(metadata)
  metadata = problem_filter.Meta(metadata)
  return metadata, required_text(metadata.language, "language metadata")
end

local function latex_path(path)
  return path:gsub("\\", "/")
end

local function Pandoc(document)
  local contest_language
  document.meta, contest_language = normalize_language(document.meta)
  local contest_show_metadata = document.meta["show-metadata"]
  required_text(document.meta.name, "contest name metadata")
  required_text(document.meta.date, "contest date metadata")

  local problems = document.meta.problems
  if problems == nil or #problems == 0 then
    error("contest metadata must contain a non-empty 'problems' list", 0)
  end

  local manifest = PANDOC_STATE.input_files[1]
  if manifest == nil or manifest == "-" then
    error("the contest manifest must be read from a file", 0)
  end
  local manifest_directory = pandoc.path.directory(manifest)
  local fragment_directory = metadata_text(document.meta["fragments-dir"])
    or "build/problems"
  local template_path = metadata_text(document.meta["problem-template"])
    or pandoc.path.join({script_directory, "problem.template.tex"})
  local problem_template = pandoc.template.compile(read_file(template_path))
  local writer_options = pandoc.WriterOptions({template = problem_template})

  local output = {}
  local used_indices = {}
  for number, item in ipairs(problems) do
    local source = required_text(item.source, "problem source")
    local source_path = source
    if pandoc.path.is_relative(source_path) then
      source_path = pandoc.path.join({manifest_directory, source_path})
    end
    source_path = pandoc.path.normalize(source_path)

    local index = metadata_text(item.index) or alphabetical_index(number)
    if not index:match("^[%w]+$") then
      error("invalid problem index '" .. index .. "' in '" .. source .. "'", 0)
    end
    if used_indices[index] then
      error("duplicate problem index '" .. index .. "'", 0)
    end
    used_indices[index] = true

    local problem = pandoc.read(
      read_file(source_path),
      "markdown-implicit_figures+fenced_divs+fenced_code_attributes",
      pandoc.ReaderOptions({standalone = true})
    )
    if problem.meta.language == nil then
      problem.meta.language = pandoc.MetaString(contest_language)
    end
    if item["show-metadata"] ~= nil then
      problem.meta["show-metadata"] = item["show-metadata"]
    elseif problem.meta["show-metadata"] == nil then
      problem.meta["show-metadata"] = contest_show_metadata
    end
    local problem_language
    problem.meta, problem_language = normalize_language(problem.meta)
    if problem_language ~= contest_language then
      error(
        "problem '" .. source .. "' uses language '" .. problem_language
          .. "', but the contest uses '" .. contest_language .. "'",
        0
      )
    end
    required_text(problem.meta.title, "title metadata in '" .. source .. "'")

    problem = problem_filter.Pandoc(problem)
    local fragment = pandoc.write(problem, "latex", writer_options)
    local fragment_path = pandoc.path.join({fragment_directory, index .. ".tex"})
    write_file(fragment_path, fragment)

    local asset_directory = latex_path(pandoc.path.directory(source_path))
    output[#output + 1] = pandoc.RawBlock("latex", table.concat({
      "\\begingroup",
      "\\def\\ProblemIndex{" .. index .. "}",
      "\\graphicspath{{" .. asset_directory .. "/}}",
      "\\input{" .. latex_path(fragment_path) .. "}",
      "\\endgroup",
    }, "\n"))
  end

  document.blocks = output
  document.meta.problems = nil
  return document
end

return {Pandoc = Pandoc}
