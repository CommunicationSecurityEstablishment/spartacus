//This C program shows the various sections of the C language that the Capua compiler supports
//This of course includes single line comments

//multiple functions
int add(int a, int b){
    return a + b;
}
int main(){
    //Regular integer variable assignment
    int a = 5;
    int b = 10;
    //Integer pointer variable
    int *c;
    //Integer array
    int d[3] = {1,2,3};
    //Referencing memory address to pointer variable
    c = &a;
    //while loop
    while (a < (b*4) - 5){ //in-line comments are also possible
        a = a + 1;
    }
    //if statement + binary operator
    if (a > 5 || b < 10){
        //nested statements (if/while)
        while (b > 4){
            b = b - 1;
        }
        a = 1;
    }
    //assigning value to array index
    d[0] = a;
    //assinging integer to value at array index
    b = d[2];
    //char variable assignment
    char e = 'z';
    //use of single/double quotes for char value
    e = "f";
    //math expression with multiple operands, parentheses (max 7 operands)
    a = (b*4) - a / 3 - (b + 4 * d[1]);
    //assigning immediate value to pointer variable
    *c = 40000000;
    //dereferencing pointer, assigning value to variable
    b = *c;
    //assigning returned value from function call to variable
    int g = add(a,b);
    //lenient syntax for spaces/newline
    int x = 5; int y=6+5+6+ a      ;
    //return statement
    return 0;
}
