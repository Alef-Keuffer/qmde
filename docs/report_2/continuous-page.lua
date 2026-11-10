-- Measures how wide a Continuous Page needs to be (the variablewidth option).
--
-- A line counts at its natural width when it ends in fill glue (headings,
-- centred text, a paragraph's last line); a justified line wants the full
-- text width. Displayed equations count at their own width; a numbered one
-- wants the full width, since its number sits at the right edge.

local HLIST, VLIST, RULE = node.id("hlist"), node.id("vlist"), node.id("rule")
local LINE, EQUATION, EQNO = 1, 6, 7
local RUNNING = -1073741824
local full

local natural_vlist

local function natural_line(line)
	if line.glue_order == 0 and line.glue_set ~= 0 then full = true end
	if not line.list then return 0 end
	local w = node.dimensions(line.list)
	-- A minipage counts at the width of its content, not its declared width.
	for n in node.traverse_id(VLIST, line.list) do
		w = w - n.width + natural_vlist(n.list)
	end
	return w
end

function natural_vlist(head)
	local w = 0
	for n in node.traverse(head) do
		local x = 0
		if n.id == HLIST then
			if n.subtype == LINE then x = n.shift + natural_line(n)
			elseif n.subtype == EQUATION then x = n.width
			elseif n.subtype == EQNO then full = true
			else x = n.shift + n.width end
		elseif n.id == VLIST then x = n.shift + natural_vlist(n.list)
		elseif n.id == RULE and n.width ~= RUNNING then x = n.width
		end
		if x > w then w = x end
	end
	return w
end

local cp = {}

-- Prints the width (in sp) the content of box register `box` needs,
-- at most `max`.
function cp.width(box, max)
	full = false
	local w = natural_vlist(tex.box[box].list)
	if full or w > max then w = max end
	tex.sprint(w)
end

return cp
