-- Convert semantic Markdown constructs to olymp.sty problem-statement macros.

local language_aliases = {
  zh = "chinese",
  ["zh-cn"] = "chinese",
  en = "english",
}

local function metadata_boolean(value, default, name)
  if value == nil then
    return default
  end
  if type(value) == "boolean" then
    return value
  end

  local text = pandoc.utils.stringify(value):lower()
  if text == "true" then
    return true
  end
  if text == "false" then
    return false
  end
  error("metadata '" .. name .. "' must be true or false", 0)
end

local function Meta(metadata)
  local language = "chinese"
  if metadata.language then
    language = pandoc.utils.stringify(metadata.language):lower()
    language = language_aliases[language] or language
  end

  if language ~= "chinese" and language ~= "english" then
    error(
      "unsupported metadata language '" .. language
        .. "' (expected 'chinese' or 'english')",
      0
    )
  end

  metadata.language = pandoc.MetaString(language)
  if language == "chinese" then
    metadata["olymp-language"] = pandoc.MetaString("chinese")
  else
    metadata["olymp-language"] = nil
  end
  metadata["show-metadata"] = pandoc.MetaBool(metadata_boolean(
    metadata["show-metadata"],
    true,
    "show-metadata"
  ))

  return metadata
end

local section_commands = {
  background = "Background",
  specification = "Specification",
  input = "InputFile",
  output = "OutputFile",
  interaction = "Interaction",
  scoring = "Scoring",
  constraints = "Constraints",
  explanation = "Explanation",
  illustration = "Illustration",
  note = "Note",
  notes = "Notes",

  ["背景知识"] = "Background",
  ["题目要求"] = "Specification",
  ["输入格式"] = "InputFile",
  ["输出格式"] = "OutputFile",
  ["交互"] = "Interaction",
  ["评分"] = "Scoring",
  ["约束"] = "Constraints",
  ["样例解释"] = "Explanation",
  ["样例说明"] = "Explanation",
  ["图表说明"] = "Illustration",
  ["提示"] = "Note",
}

local hidden_sections = {
  description = true,
  legend = true,
  statement = true,
  ["题目描述"] = true,
}

local function normalized_heading(heading)
  if heading.identifier ~= "" then
    local identifier = heading.identifier:lower()
    if section_commands[identifier] or hidden_sections[identifier] then
      return identifier
    end
  end
  return pandoc.utils.stringify(heading.content):lower()
end

local function Header(heading)
  local name = normalized_heading(heading)
  if hidden_sections[name] then
    return {}
  end

  local command = section_commands[name]
  if command then
    return pandoc.RawBlock("latex", "\\" .. command)
  end
end

local tex_escapes = {
  ["\\"] = "\\textbackslash{}",
  ["{"] = "\\{",
  ["}"] = "\\}",
  ["$"] = "\\$",
  ["&"] = "\\&",
  ["#"] = "\\#",
  ["%"] = "\\%",
  ["_"] = "\\_",
  ["~"] = "\\textasciitilde{}",
  ["^"] = "\\textasciicircum{}",
  ["\t"] = "    ",
}

local function escape_sample(text)
  return (text:gsub(".", function(character)
    return tex_escapes[character] or character
  end))
end

local function has_class(block, class_name)
  for _, class in ipairs(block.classes) do
    if class == class_name then
      return true
    end
  end
  return false
end

local function sample_error(message)
  error("invalid .samples block: " .. message, 0)
end

local function Div(div)
  if not div.classes:includes("samples") then
    return nil
  end
  if #div.content == 0 then
    sample_error("at least one input/output pair is required")
  end
  if #div.content % 2 ~= 0 then
    sample_error("each input code block must be followed by an output code block")
  end

  local rows = {}
  for index = 1, #div.content, 2 do
    local input = div.content[index]
    local output = div.content[index + 1]
    if input.t ~= "CodeBlock" or not has_class(input, "input") then
      sample_error("block " .. index .. " must be a fenced code block with class .input")
    end
    if output.t ~= "CodeBlock" or not has_class(output, "output") then
      sample_error("block " .. (index + 1) .. " must be a fenced code block with class .output")
    end

    rows[#rows + 1] = string.format(
      "\\exmp{%s\n}{%s\n}%%",
      escape_sample(input.text),
      escape_sample(output.text)
    )
  end

  local section = #rows == 1 and "\\Example" or "\\Examples"
  local latex = table.concat({
    section,
    "\\begin{example}",
    table.concat(rows, "\n"),
    "\\end{example}",
  }, "\n")
  return pandoc.RawBlock("latex", latex)
end

local function Para(paragraph)
  if #paragraph.content ~= 1 or paragraph.content[1].t ~= "Image" then
    return nil
  end

  -- Standalone statement images should stay where the author put them.  The
  -- reader has implicit figures disabled to prevent LaTeX floats from moving
  -- above the problem header, so restore the centering that figures provided
  -- without turning the image back into a float.
  return pandoc.Blocks({
    pandoc.RawBlock("latex", "\\begin{center}"),
    paragraph,
    pandoc.RawBlock("latex", "\\end{center}"),
  })
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

local function Pandoc(document)
  local statement = pandoc.Blocks({})
  for _, block in ipairs(document.blocks) do
    if is_tutorial_heading(block) then
      break
    end
    statement:insert(block)
  end
  document.blocks = statement
  return document:walk({
    Header = Header,
    Div = Div,
    Para = Para,
  })
end

return {
  Meta = Meta,
  Pandoc = Pandoc,
}
