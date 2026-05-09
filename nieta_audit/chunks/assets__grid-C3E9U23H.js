const s=i=>{const{containerWidth:t,gap:c,padding:e,minCount:n=3}=i,r=(()=>t>=1024?n+3:t>=768?n+2:t>=576?n+1:n)(),o=(t-e*2-(r-1)*c)/r;return{cols:r,itemWidth:o}};export{s as c};
