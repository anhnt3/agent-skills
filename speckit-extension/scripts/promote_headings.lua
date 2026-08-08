-- Nâng đoạn văn thành Header theo danh sách nạp qua --metadata-file,
-- và gỡ vỏ Div/Span mang custom-style do `-f docx+styles` sinh ra.
-- KHÔNG dùng pandoc.json (chỉ có ở bản pandoc mới): --metadata-file đã tự
-- phân giải JSON thành MetaList/MetaMap sẵn.
local promotions = {}
local matched = {}
local expected = 0
local promoted = 0

local function normalize(s)
  return (s:gsub("%s+", " "):gsub("^%s*(.-)%s*$", "%1"))
end

function Meta(meta)
  if meta.promotions == nil then return nil end
  for _, item in ipairs(meta.promotions) do
    local text = pandoc.utils.stringify(item.text)
    local level = math.tointeger(tonumber(pandoc.utils.stringify(item.level)))
    local key = normalize(text)
    if promotions[key] == nil then expected = expected + 1 end
    promotions[key] = level
  end
  return nil
end

function Para(el)
  local key = normalize(pandoc.utils.stringify(el))
  local level = promotions[key]
  if level then
    if not matched[key] then
      matched[key] = true
      promoted = promoted + 1
    end
    return pandoc.Header(level, el.content)
  end
  return nil
end

function Div(el)
  if el.attributes["custom-style"] then return el.content end
  return nil
end

function Span(el)
  if el.attributes["custom-style"] then return el.content end
  return nil
end

function Pandoc(doc)
  if expected > 0 and promoted ~= expected then
    local missing = {}
    for key, _ in pairs(promotions) do
      if not matched[key] then missing[#missing + 1] = key end
    end
    table.sort(missing)
    error(string.format(
      "promote_headings: nâng được %d/%d tiêu đề — danh sách promotions không khớp tài liệu.\n"
      .. "Không nâng được (thường là đoạn nằm trong ô bảng):\n  %s",
      promoted, expected, table.concat(missing, "\n  ")))
  end
  return doc
end

return {
  { Meta = Meta },
  { Div = Div, Span = Span, Para = Para },
  { Pandoc = Pandoc },
}
