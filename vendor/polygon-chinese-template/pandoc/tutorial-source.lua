-- Extract a trailing tutorial section from a problem Markdown document and
-- optionally combine every problem referenced by a contest manifest.

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

local function alphabetical_index(number)
  local result = ""
  while number > 0 do
    local remainder = (number - 1) % 26
    result = string.char(string.byte("A") + remainder) .. result
    number = math.floor((number - 1) / 26)
  end
  return result
end

local function input_path()
  local path = PANDOC_STATE.input_files[1]
  if path == nil or path == "-" then
    error("tutorial input must be read from a file", 0)
  end
  return path
end

local tutorial_titles = {
  tutorial = true,
  solution = true,
  ["题解"] = true,
  ["题目解答"] = true,
}

local function is_tutorial_heading(block)
  if block.t ~= "Header" or block.level ~= 1 then
    return false
  end
  local identifier = block.identifier:lower()
  if identifier == "tutorial" or identifier == "solution" then
    return true
  end
  return tutorial_titles[pandoc.utils.stringify(block.content):lower()] == true
end

local function tutorial_slides(
  problem,
  description,
  frame_level,
  frame_title,
  source_path,
  identifier_prefix
)
  local marker
  for index, block in ipairs(problem.blocks) do
    if is_tutorial_heading(block) then
      if marker ~= nil then
        error("multiple tutorial headings in " .. description, 0)
      end
      marker = index
    end
  end
  if marker == nil then
    error("missing '# 题解 {#tutorial}' section in " .. description, 0)
  end

  local tutorial = pandoc.Blocks({})
  for index = marker + 1, #problem.blocks do
    tutorial:insert(problem.blocks[index])
  end
  if #tutorial == 0 or tutorial[1].t ~= "Header" or tutorial[1].level ~= 2 then
    error(
      "tutorial section in " .. description
        .. " must start with a level-2 heading",
      0
    )
  end

  local source_directory = pandoc.path.directory(source_path)
  tutorial = tutorial:walk({
    Header = function(header)
      if header.level == 1 then
        error(
          "tutorial section must be the final level-1 section in "
            .. description,
          0
        )
      end
      if header.level > 2 then
        header.level = header.level + frame_level - 2
      end
      if identifier_prefix ~= nil and header.identifier ~= "" then
        header.identifier = identifier_prefix .. "-" .. header.identifier
      end
      return header
    end,
    Image = function(image)
      local target = image.src
      local is_uri = target:match("^%a[%w+.-]*:") ~= nil
      if not is_uri and target:sub(1, 1) ~= "#"
          and pandoc.path.is_relative(target) then
        image.src = pandoc.path.normalize(pandoc.path.join({
          source_directory,
          target,
        }))
      end
      return image
    end,
  })

  local slides = pandoc.Blocks({})
  local heading
  local content = pandoc.Blocks({})
  local function flush_slide()
    if heading == nil then
      return
    end
    local attributes = {}
    for key, value in pairs(heading.attributes) do
      attributes[key] = value
    end
    local frame = pandoc.Header(
      frame_level,
      frame_title,
      pandoc.Attr(heading.identifier, heading.classes, attributes)
    )
    slides:insert(frame)
    slides:extend(content)
  end

  for _, block in ipairs(tutorial) do
    if block.t == "Header" and block.level == 2 then
      flush_slide()
      heading = block
      content = pandoc.Blocks({})
    else
      content:insert(block)
    end
  end
  flush_slide()
  return slides
end

local function single_problem(document)
  local source = input_path()
  local title = required_text(document.meta.title, "problem title metadata")
  document.blocks = tutorial_slides(
    document,
    "problem source '" .. source .. "'",
    1,
    title,
    source
  )
  if document.meta.subtitle == nil then
    document.meta.subtitle = pandoc.MetaString("题解")
  end
  return document
end

local function contest(document)
  local manifest = input_path()
  local manifest_directory = pandoc.path.directory(manifest)
  local problems = document.meta.problems
  if problems == nil or #problems == 0 then
    error("contest metadata must contain a non-empty 'problems' list", 0)
  end

  document.meta.title = document.meta.name
  required_text(document.meta.title, "contest name metadata")
  if document.meta.subtitle == nil then
    document.meta.subtitle = pandoc.MetaString("命题报告")
  end

  local output = pandoc.Blocks({})
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
    local title = required_text(
      problem.meta.title,
      "title metadata in '" .. source .. "'"
    )
    local section_title = index .. ". " .. title
    local blocks = tutorial_slides(
      problem,
      "problem source '" .. source .. "'",
      2,
      section_title,
      source_path,
      "problem-" .. index:lower()
    )

    output:insert(pandoc.Header(1, section_title))
    output:extend(blocks)
  end

  document.blocks = output
  document.meta.problems = nil
  return document
end

local function Pandoc(document)
  local mode = required_text(document.meta["tutorial-mode"], "tutorial mode")
  document.meta["tutorial-mode"] = nil
  if mode == "problem" then
    return single_problem(document)
  end
  if mode == "contest" then
    return contest(document)
  end
  error("unsupported tutorial mode '" .. mode .. "'", 0)
end

return {Pandoc = Pandoc}
