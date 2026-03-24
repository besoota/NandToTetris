// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.

//R0...whether scrren is now black or not.
//R1...whether key is pressed or not.
@8192
D=A
@nrow
M=D
@R0
M=0

(LOOP)
    //if KBD==0 goto NotPush
    @KBD
    D=M
    @NotPush
    D;JEQ
(PUSH)
    //R1=1
    @R1
    M=1
    //goto Check
    @Check
    0;JMP

(NotPush)
    //R1=0
    @R1
    M=0

(Check)
    //if(R0==R1) goto Filled
    @R0
    D=M
    @R1
    D=D-M
    @Filled
    D;JEQ

//i=0
@i
M=0
//if(R1==0) goto PaintWh
@R1
D=M
@PaintWh
D;JEQ
(PaintBl)
    //if i==nrow goto Filled
    @i
    D=M
    @nrow
    D=D-M
    @Filled
    D;JEQ
    //*(SC+i)=-1
    @SCREEN
    D=A
    @i
    A=D+M
    M=-1
    //i++
    @i
    M=M+1
    //goto PaintBl
    @PaintBl
    0;JMP

(PaintWh)
    //if i==nrow goto Filled
    @i
    D=M
    @nrow
    D=D-M
    @Filled
    D;JEQ
    //*(SC+i)=0
    @SCREEN
    D=A
    @i
    A=D+M
    M=0
    //i++
    @i
    M=M+1
    //goto PaintWh
    @PaintWh
    0;JMP
(Filled)
    //R0=R1
    @R1
    D=M
    @R0
    M=D
    //goto LOOP
    @LOOP
    0;JMP

    
