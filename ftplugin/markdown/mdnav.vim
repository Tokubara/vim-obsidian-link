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

command! MDNavExec execute 'py3file ' . g:mdnav#PythonScript
command! GenLinkLine call s:GenLink("line") 
command! GenLinkID call s:GenLink("id") 
command! GenLinkEmpty call s:GenLink("") 
command! GenLinkHeading call s:GenLink("heading") 
command! GenLinkSuffix call s:GenLink("suffix") 
nnoremap <buffer> <CR> :MDNavExec<CR>

