#!/usr/bin/env python3
"""Replace static publication content inside year tabs with empty placeholders."""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / 'Pages' / 'publications.html'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Start: first year tab (2026) opening and its __content opening
start_marker = '<div data-title="&lt;strong&gt;2026&lt;/strong&gt;" class="wp-block-themeisle-blocks-tabs-item"><div class="wp-block-themeisle-blocks-tabs-item__header" tabindex="0"><strong>2026</strong></div><div class="wp-block-themeisle-blocks-tabs-item__content">'
# End: just before the first category tab (Spatio-Temporal Data Mining)
end_marker = '<div data-title="&lt;strong&gt;Spatio-Temporal Data Mining&lt;/strong&gt;" class="wp-block-themeisle-blocks-tabs-item" data-pub-filter="stm">'

i = content.find(start_marker)
j = content.find(end_marker)
if i == -1 or j == -1:
    raise SystemExit('Markers not found')
# Include the closing </div></div> of the Before 2020 tab (so we don't remove the inner tabs closing tags)
# The content we replace ends right before end_marker. So we replace from i to j-1 (to leave newline/space if any).
# Actually: from i we want to replace until (but not including) end_marker. So replace content[i:j] with new shell.
# After the last year tab we need </div></div> to close the Before 2020 tab. So the "new shell" is 8 year tabs.
# Each tab: opening line + newline + </div> (close __content) + newline + </div> (close tab item). So 4 lines per tab for 2025..Before 2020, and 2026 is the first so same.
# Wait - the first year tab starts with start_marker which is the opening tag and the __content div opening. So there's no newline in the marker. So the marker is one long line. After it comes the content (many divs). So we replace from i (start of marker) to j (start of next tab). So the replacement is: start_marker + newline + empty content closing + 7 more year tabs. So:
# start_marker already opens 2026 and its __content. So we need: \n</div>\n</div>\n then 2025 tab same, ... then Before 2020 tab \n</div>\n</div>
year_tabs = [
    ('2025', '2025'),
    ('2024', '2024'),
    ('2023', '2023'),
    ('2022', '2022'),
    ('2021', '2021'),
    ('2020', '2020'),
    ('Before 2020', 'Before 2020'),
]
new_shell = start_marker + '\n</div>\n</div>\n'
for label, strong in year_tabs:
    new_shell += f'<div data-title="&lt;strong&gt;{strong}&lt;/strong&gt;" class="wp-block-themeisle-blocks-tabs-item"><div class="wp-block-themeisle-blocks-tabs-item__header" tabindex="0"><strong>{label}</strong></div><div class="wp-block-themeisle-blocks-tabs-item__content">\n</div>\n</div>\n'
# Now we have 2026 (opened in start_marker, closed with </div></div>) and 2025..Before 2020. Good.
new_content = content[:i] + new_shell + content[j:]
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Replaced static publication HTML with empty year tab shell.')
