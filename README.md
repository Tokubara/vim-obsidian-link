Based on [this repo](https://github.com/chmp/mdnav)

Jump to and generate wikilinks for obsidian notes in vim/neovim.

Support following links:
- `[[^ieYae2]]`
- `[[#heading]]`
- `[[perl#heading]]`, `[[perl.md#heading]]`(.md extension can be omitted)
- `[[perl#^ieYae2]]`
- `[[/Users/quebec/a.py:32]]`, line number
- `[[picture.png]]`, open in system apps

Press enter key to navigate.

You can generate links with `:GenLinkID`(generate `[[^ieYae2]]`), `:GenLinkLine`(generate  `[[/Users/quebec/a.py:32]]`), `:GenLinkHeading`(generate `[[perl#heading]]`), `:GenLinkEmpty`(generate `[[/Users/quebec/a.py]]`)

I have problems with importing modules. So in mdnav.py, I write `sys.path.append("/Users/quebec/box/obsidian/vim/mdnav/ftplugin/markdown/")`, this should be changed to your path(Or tell me how to fix this, thanks).
You can change commands and maps in mdnav.vim.

`open_in_os_extensions` in `parse_path` determines which extensions should be opened with system apps. I should write in mdnav.vim, but I have not fixed it.

