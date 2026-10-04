"""Il simbolo del Progetto dei Cerchi: sette anelli uguali in catena chiusa, uno evidenziato.
Ogni anello passa sopra un vicino e sotto l'altro: nessuno sta sopra tutti."""
import math
CARTA,INK,ACC,CEN,CEN_S='#f3f5f1','#17211d','#0e6656','#c98f1c','#e3b24a'
def inter(c1,r1,c2,r2):
    (x1,y1),(x2,y2)=c1,c2; d=math.hypot(x2-x1,y2-y1)
    a=(r1*r1-r2*r2+d*d)/(2*d); h=math.sqrt(r1*r1-a*a); xm=x1+a*(x2-x1)/d; ym=y1+a*(y2-y1)/d
    return [(xm+h*(y2-y1)/d,ym-h*(x2-x1)/d),(xm-h*(y2-y1)/d,ym+h*(x2-x1)/d)]
def arco(c,r,th,dl,col,w):
    a0,a1=th-dl,th+dl
    return '<path d="M%.2f %.2fA%s %s 0 0 1 %.2f %.2f" fill="none" stroke="%s" stroke-width="%s"/>'%(c[0]+r*math.cos(a0),c[1]+r*math.sin(a0),r,r,c[0]+r*math.cos(a1),c[1]+r*math.sin(a1),col,w)
def corona(c,r,w):
    def cerchio(R): return 'M%.2f %.2fa%s %s 0 1 0 %.2f 0a%s %s 0 1 0 %.2f 0z'%(c[0]-R,c[1],R,R,2*R,R,R,-2*R)
    return cerchio(r+w/2+1)+cerchio(r-w/2-1)
def simbolo(size=1080,n=7,dist=245,r=140,w=34,bg=ACC,anello=CARTA,uno=CEN_S,sfondo=True,scala=1.0):
    C=size/2; dist*=scala; r*=scala; w*=scala; gap=w*0.24
    R=[((C+dist*math.cos(-math.pi/2+2*math.pi*i/n),C+dist*math.sin(-math.pi/2+2*math.pi*i/n)),r,(uno if i==0 else anello)) for i in range(n)]
    defs=''.join('<clipPath id="k%d"><path clip-rule="evenodd" d="%s"/></clipPath>'%(i,corona(c,rr,w)) for i,(c,rr,_) in enumerate(R))
    out=''.join('<circle cx="%.2f" cy="%.2f" r="%s" fill="none" stroke="%s" stroke-width="%s"/>'%(c[0],c[1],rr,col,w) for c,rr,col in R)
    for i in range(n):
        j=(i+1)%n
        P=sorted(inter(R[i][0],r,R[j][0],r),key=lambda p:-math.hypot(p[0]-C,p[1]-C))   # prima l'incrocio esterno
        for k,p in enumerate(P):
            sopra,sotto=(i,j) if k==0 else (j,i)       # all'esterno passa sopra l'anello i, all'interno il successivo
            c,rr,col=R[sopra]; th=math.atan2(p[1]-c[1],p[0]-c[0]); span=w*1.25
            out+='<g clip-path="url(#k%d)">%s</g>'%(sotto,arco(c,rr,th,span/rr,bg,w+2*gap))   # apre il varco nell'anello che passa sotto
            out+=arco(c,rr,th,span/rr,col,w)                                                 # e ridisegna sopra l'altro
    fondo='<rect width="%d" height="%d" fill="%s"/>'%(size,size,bg) if sfondo else ''
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"><defs>%s</defs>%s%s</svg>'%(size,size,size,size,defs,fondo,out)
if __name__=='__main__':
    open('simbolo_scuro.svg','w').write(simbolo())
    open('simbolo_chiaro.svg','w').write(simbolo(bg=CARTA,anello=ACC,uno=CEN))
    print('ok')
