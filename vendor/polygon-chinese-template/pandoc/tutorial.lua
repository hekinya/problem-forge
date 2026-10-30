-- Add a small, explicit Markdown vocabulary for Beamer tutorial slides.

local block_environments = {
  block = "block",
  alertblock = "alertblock",
  exampleblock = "exampleblock",
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
  metadata["title-page"] = pandoc.MetaBool(metadata_boolean(
    metadata["title-page"],
    true,
    "title-page"
  ))
  return metadata
end

local function required_title(div, class_name)
  local title = div.attributes.title
  if title == nil or title == "" then
    error(
      "tutorial ." .. class_name .. " block requires a title attribute",
      0
    )
  end

  local parsed = pandoc.read(title, "markdown")
  local block = parsed.blocks[1]
  if #parsed.blocks ~= 1 or (block.t ~= "Para" and block.t ~= "Plain") then
    error("tutorial block title must contain inline Markdown only", 0)
  end
  return pandoc.write(
    pandoc.Pandoc({pandoc.Plain(block.content)}),
    "latex"
  ):gsub("%s+$", "")
end

local function Div(div)
  for class_name, environment in pairs(block_environments) do
    if div.classes:includes(class_name) then
      local title = required_title(div, class_name)
      local blocks = pandoc.List({
        pandoc.RawBlock(
          "latex",
          "\\begin{" .. environment .. "}{" .. title .. "}"
        ),
      })
      blocks:extend(div.content)
      blocks:insert(pandoc.RawBlock("latex", "\\end{" .. environment .. "}"))
      return blocks
    end
  end
end

return {
  Meta = Meta,
  Div = Div,
}
