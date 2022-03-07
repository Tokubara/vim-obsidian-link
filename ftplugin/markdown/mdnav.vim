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
  if exists("t:genlink_local")
    let t:genlink_local = 1 - t:genlink_local
  else
    let t:genlink_local = 1
  endif
endfunction

command! MDNavExec execute 'py3file ' . g:mdnav#PythonScript
command! GenLinkLine call s:GenLink("line") 
command! GenLinkID call s:GenLink("id") 
command! GenLinkEmpty call s:GenLink("empty") 
command! GenLinkHeading call s:GenLink("heading") 
command! GenLinkSuffix call s:GenLink("suffix") 
command! GenLinkToggleLocal call s:GenLinkToggleLocal()
nnoremap <buffer> <CR> :MDNavExec<CR>

