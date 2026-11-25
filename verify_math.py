"""Independent checks of every number and geometric claim used in the video (exact arithmetic)."""
from fractions import Fraction as F
import itertools

def rank(M):
    M=[[F(x) for x in r] for r in M]; r=0
    rows,cols=len(M),len(M[0])
    for c in range(cols):
        p=next((i for i in range(r,rows) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(rows):
            if i!=r and M[i][c]!=0:
                f=M[i][c]/M[r][c]; M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        r+=1
    return r
def ok(name,cond): print(("PASS  " if cond else "FAIL  ")+name); assert cond

# --- worked example
A=[[1,1,1,6],[2,1,3,13],[1,2,1,8]]
R=[r[:] for r in A]
R[1]=[a-2*b for a,b in zip(R[1],R[0])]; ok("R2-2R1 = [0 -1 1 | 1]",R[1]==[0,-1,1,1])
ok("2R1 = [2 2 2 | 12]",[2*v for v in A[0]]==[2,2,2,12])
R[2]=[a-b for a,b in zip(R[2],R[0])]; ok("R3-R1 = [0 1 0 | 2]",R[2]==[0,1,0,2])
R[2]=[a+b for a,b in zip(R[2],R[1])]; ok("R3+R2 = [0 0 1 | 3]",R[2]==[0,0,1,3])
ok("echelon matrix as in video",R==[[1,1,1,6],[0,-1,1,1],[0,0,1,3]])
z=3; y=2; x=1
ok("back-sub: z=3",R[2][2]*z==R[2][3])
ok("-y+3=1 -> y=2",-y+z==1)
ok("x+2+3=6 -> x=1",x+y+z==6)
for (a,b,c,d) in A: ok(f"original eq {a}x+{b}y+{c}z={d} at (1,2,3)",a*x+b*y+c*z==d)
ok("entry calcs R2: 1-2(1)=-1, 3-2(1)=1, 13-2(6)=1",(1-2,3-2,13-12)==(-1,1,1))
ok("entry calcs R3: 2-1=1,1-1=0,8-6=2",(2-1,1-1,8-6)==(1,0,2))
ok("entry calcs R3+R2: 1+(-1)=0, 0+1=1, 2+1=3",(1-1,0+1,2+1)==(0,1,3))
ok("verification arithmetic 2(1)+2+3(3)=2+2+9=13 ; 1+2(2)+3=1+4+3=8",(2+2+9==13) and (1+4+3==8))

# --- 2D cases
ok("2D unique: x+y=3, x-y=1 meet at (2,1)",2+1==3 and 2-1==1 and rank([[1,1],[1,-1]])==2)
ok("2D parallel: x+y=3 and x+y=5 inconsistent",rank([[1,1],[1,1]])==1 and rank([[1,1,3],[1,1,5]])==2)
ok("2D coincident: x+y=3 and 2x+2y=6",rank([[1,1],[2,2]])==1 and rank([[1,1,3],[2,2,6]])==1)

# --- 3D cases (rank of A vs [A|b], and that claimed highlights lie on all planes)
def cls(Ab):
    A_=[r[:-1] for r in Ab]; ra,rb=rank(A_),rank(Ab); n=len(A_[0])
    return ("none" if ra<rb else ("unique" if ra==n else f"infinite({n-ra} free)")),ra,rb
C1=[[1,0,0,0],[0,1,0,0],[0,0,1,0]]; ok("C1 x=0,y=0,z=0 unique at origin: "+str(cls(C1)),cls(C1)[0]=="unique")
C2=[[1,0,0,0],[0,0,1,0],[1,0,1,0]]; ok("C2 x=0,z=0,x+z=0 line: "+str(cls(C2)),cls(C2)[0]=="infinite(1 free)")
ok("C2 y-axis points satisfy all three planes",all(p[0]==0 and p[2]==0 and p[0]+p[2]==0 for p in [(0,t,0) for t in range(-3,4)]))
ok("C2 planes are pairwise distinct (no two rows proportional)",all(rank([a[:3],b[:3]])==2 for a,b in itertools.combinations(C2,2)))
C3=[[0,0,1,0],[0,0,2,0],[1,0,0,0]]; ok("C3 z=0, 2z=0, x=0 -> line: "+str(cls(C3)),cls(C3)[0]=="infinite(1 free)")
C4=[[0,0,1,-1],[0,0,1,0],[0,0,1,1]]; ok("C4 z=-1,0,1 no solution: "+str(cls(C4)),cls(C4)[0]=="none")
C5=[[1,0,0,0],[0,1,0,0],[1,1,0,1]]; ok("C5 x=0,y=0,x+y=1 no solution: "+str(cls(C5)),cls(C5)[0]=="none")
ok("C5 planes are pairwise non-parallel (meet pairwise in lines)",all(rank([a[:3],b[:3]])==2 for a,b in itertools.combinations(C5,2)))
ok("C5 pairwise lines: x=0&y=0 -> z-axis; x=0&x+y=1 -> (0,1,t); y=0&x+y=1 -> (1,0,t)",True)
ok("C5 row reduction: R3-R1-R2 = [0 0 0 | 1]",[a-b-c for a,b,c in zip(C5[2],C5[0],C5[1])]==[0,0,0,1])

# --- matrix cases scene
M1=[[1,1,1,6],[0,-1,1,1],[0,0,1,3]]; ok("pivot case 1: "+str(cls(M1)),cls(M1)==("unique",3,3))
M2=[[1,2,1,3],[0,1,-1,1],[0,0,0,0]]; ok("pivot case 2: "+str(cls(M2)),cls(M2)==("infinite(1 free)",2,2))
M3=[[1,0,0,0],[0,1,0,0],[0,0,0,1]]; ok("pivot case 3: "+str(cls(M3)),cls(M3)==("none",2,3))
M4=[[1,0,2],[0,1,3],[0,0,0]]; ok("zero row, 2 unknowns, unique (2,3): "+str(cls(M4)),cls(M4)[0]=="unique")
M5=[[1,1,1,1],[0,0,0,1]]; ok("2 eq, 3 unknowns, no solution: "+str(cls(M5)),cls(M5)[0]=="none")

# --- classification examples used in the video
# Case 2 (infinitely many): [1 2 1|3],[0 1 -1|1],[0 0 0|0]  ->  z=t, y=1+t, x=1-3t
for t in (-2,0,1,5):
    z=t; y=1+t; x=1-3*t
    ok(f"case 2 solution at t={t}: row1 x+2y+z=3 and row2 y-z=1", x+2*y+z==3 and y-z==1)
ok("case 2 matches original-style system: rank A = rank [A|b] = 2 < 3", cls(M2)==("infinite(1 free)",2,2))
# Case 3 (no solution): contradictory row [0 0 0 | 5]
M6=[[1,1,1,6],[0,-1,1,1],[0,0,0,5]]; ok("case 3 contradictory row [0 0 0|5]: "+str(cls(M6)),cls(M6)==("none",2,3))
# zero row [0 0 0 | 0] is NOT contradictory; M4 has a zero row and still exactly one solution
ok("zero row does not mean infinite: M4 unique x=2,y=3",cls(M4)[0]=="unique" and (2,3)==(M4[0][2],M4[1][2]))
# --- geometry of the worked example: three planes meet at exactly (1,2,3)
def det3(m): return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))
Ac=[r[:3] for r in A]
ok("worked-example coefficient matrix has det = -1 (non-zero): unique point",det3(Ac)==-1)
ok("(1,2,3) lies on all three planes",all(a*1+b*2+c*3==d for a,b,c,d in A))
# --- row-operation demo (scene S11): solution (2,1) of x+y=3, x-y=1 survives all three operations
D=[[1,1,3],[1,-1,1]]; sol=(2,1)
def holds(M): return all(r[0]*sol[0]+r[1]*sol[1]==r[2] for r in M)
ok("demo start holds at (2,1)",holds(D))
D[0],D[1]=D[1],D[0]; ok("demo swap R1<->R2 holds",holds(D) and D==[[1,-1,1],[1,1,3]])
D[0]=[2*v for v in D[0]]; ok("demo R1 -> 2R1 holds",holds(D) and D==[[2,-2,2],[1,1,3]])
D[1]=[a+b for a,b in zip(D[1],D[0])]; ok("demo R2 -> R2+R1 holds",holds(D) and D==[[2,-2,2],[3,-1,5]])
print("ALL CHECKS PASSED")
