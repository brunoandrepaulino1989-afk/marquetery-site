# Build the claude.ai preview page (no doctype wrapper) from the built index.html.
import sys
src, out = sys.argv[1], sys.argv[2]
d=open(src).read()
head=d[d.index('<title>'):d.index('</head>')]
body=d[d.index('<body>')+6:d.rindex('</body>')]
head=head.replace('*{box-sizing:border-box}\nbody{margin:0}\nimg{max-width:100%}\n[hidden]{display:none!important}','*{box-sizing:border-box}',1)
open(out,'w').write(head+body)
