" if exists('g:mdnav#PythonScript')
"    finish
"endif

let g:mdnav#PythonScript = expand('<sfile>:r') . '.py'
let s:gen_link_script = substitute(g:mdnav#PythonScript, "mdnav\.py", "genlink.py", "")
execute 'py3 sys.path.append("' . expand("<sfile>:h")  . '")'
function! s:GenLink(argv)
  execute 'py3 sys.argv=["'.a:argv.'"]'
  execute 'py3file ' . s:gen_link_script
endfunction

function! s:GenLinkToggleLocal()
  if exists("b:genlink_local")
    let b:genlink_local = 1 - b:genlink_local
  else
    let b:genlink_local = 1
  endif
endfunction

function! s:GenLinkReload()
py3 << EOF
import parse_path
from parse_path import ParsePath, ParsedPath, ParseType
import importlib
importlib.reload(parse_path)
EOF
endfunction

command! MDNavExec execute 'py3file ' . g:mdnav#PythonScript
command! GenLinkLine call s:GenLink("line") 
command! GenLinkID call s:GenLink("id") 
command! GenLinkEmpty call s:GenLink("empty") 
command! GenLinkHeading call s:GenLink("heading") 
command! GenLinkSuffix call s:GenLink("suffix") 
command! GenLinkToggleLocal call s:GenLinkToggleLocal()
command! GenLinkReload call s:GenLinkReload()
nnoremap <buffer> <CR> :MDNavExec<CR>

