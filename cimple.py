# MARIOS IAKOVIDIS AM 4063 cs04063
# THEOFILOS-GEORGIOS PETSIOS AM 4158 cs04158
#
#                                                       CIMPLE COMPILER
# Implementation of a compiler that performs compilation of Cimple programming language code to MIPS assembly.
# The code below executes the following stages of compilation process: Lexical Analysis, Syntax Analysis, Intermediate Code Generation and C equivalent code in non funtional codes, Symbols Array, Semantic Analysis and MIPS Assembly Code Generation.
# Execute command is: python3 cimple_4063_4158.py filename (where filename is the name of a .ci file)
#####################################################################################################################################################################################

#######################################
# Import sys to get arguments from terminal
#######################################
import sys

#######################################
# Scope class that represents the nesting levels(Symbols Array)
#######################################
class Scope:
    entity = [] # Array of entities that belong to the current nesting level.
    length = 12 # Length of the function in data memory.
    def __init__(self,nestinglevel,previousscope,nextscope):
        self.nestinglevel = nestinglevel
        self.previousscope = previousscope
        self.nextscope = nextscope
        self.entity = []

#######################################
# Entity class that represents variables, constants, function and procedures (Symbols Array)
#######################################
class RecordEntity:
    arguments = [] # Array of arguments that a function/procedure uses to be called.
    framelength = 12 # Framelength of function/procedure entities.
    offset = 0 # Offset of variable entities.
    startquad = 0 # The first quad of a function/procedure entity.
    def __init__(self,name,entitytype,value,parmode):
        self.name = name
        self.entitytype = entitytype
        self.value = value
        self.parmode = parmode
        self.arguments = []

#######################################
# Argument class that represents the function/procedure arguments (Symbols Array)
#######################################
class Argument:
    def __init__(self,parmode,argumenttype,name):
        self.parmode = parmode
        self.argumenttype = argumenttype
        self.name = name

#######################################
# Add new Scope in the Symbols Array and add arguments in it if it is necessary(Symbols Array)
#######################################
def createscope():
    global lastscope # current scope
    # Add new scope in the Symbols Array.
    if lastscope is None:
        lastscope = Scope(0,None,None)
    else:
        newnestinglevel = lastscope.nestinglevel + 1
        newScope = Scope(newnestinglevel,lastscope,None)
        lastscope.nextscope = newScope
        lastscope = newScope
    # Add arguments.
    if lastscope.previousscope is not None:
        functionEntity = lastscope.previousscope.entity[-1]
        for a in functionEntity.arguments:
            addentity(a.name,"variable",None,None,a.parmode)

#######################################
# Delete a Scope from the Symbols Array, calculate the framelength of the entity that created it and add Symbols Array to an array (Symbols Array)
#######################################
def deletescope(blockName):
    global lastscope # current scope
    # Add symbol array entities to be written in an output file.
    symbols_array.append("Scope:" + blockName)
    for i in lastscope.entity:
        if i.entitytype == "variable":
            symbols_array.append("\t" + i.name + " " + str(i.offset))
        else:
            symbols_array.append("\t" + i.name + " (" + str(i.framelength) + ")")
    # Calculate the framelength of the caller function.entity.
    for e in lastscope.previousscope.entity:
        temp_entity = e
        if temp_entity.entitytype == "function" or temp_entity.entitytype == "procedure":
            if temp_entity.name == blockName:
                temp_entity.framelength = lastscope.length
                e = temp_entity
    # Delete Scope.
    lastscope.previousscope.nextscope = None
    lastscope = lastscope.previousscope

#######################################
# Add record entities in a scope in the Symbol Array (Symbols Array)
#######################################
def addentity(name,entitytype,startquad,value,parmode):
    global lastscope # current Scope.
    global block_name # name of the block that is being compiled.
    counter = 0
    if entitytype == "variable":
        for e in lastscope.entity:
            if e.entitytype == "variable":
                counter += 1
            if e.name == name:
                print("ERROR: " + name + " is defined multiple times in the same block.")
                exit()
        offset = 12 + 4*counter
        new_entity = RecordEntity(name,entitytype,value,parmode)
        new_entity.offset = offset
        lastscope.entity.append(new_entity)
        lastscope.length += 4
    elif entitytype == "function":
        for e in lastscope.entity:
            if e.name == name:
                print("ERROR: " + name + " is defined multiple times in the same block.")
                exit()
        new_entity = RecordEntity(name,entitytype,value,parmode)
        lastscope.entity.append(new_entity)
    elif entitytype == "procedure":
        for e in lastscope.entity:
            if e.name == name:
                print("ERROR: " + name + " is defined multiple times in the same block.")
                exit()
        new_entity = RecordEntity(name,entitytype,value,parmode)
        lastscope.entity.append(new_entity)

#######################################
# Add argument in an entity in the Symbol Array (Symbols Array)
#######################################
def addargument(parmode,name):
    global lastscope # current scope
    argumenttype = "int"
    functionEntity = lastscope.entity[-1]
    newArgument = Argument(parmode,argumenttype,name)
    functionEntity.arguments.append(newArgument)

#######################################
# Search for variables/functions/procedures in the Symbols Array and return the entity and its nesting level (Symbols Array)
#######################################
def searchEntity(searchName):
    global lastscope # current scope
    tempLastScope = lastscope
    while tempLastScope != None:
        for e in tempLastScope.entity:
            if e.name == searchName:
                return e,tempLastScope.nestinglevel
        tempLastScope = tempLastScope.previousscope
    print("ERROR: '" + searchName + "' is not defined.\n")
    exit()

#######################################
# Check if the return statements of the function/procedures are used as they should be used (Semantic Analysis)
#######################################
def checkReturn():
    global isfunction # boolean that indicates if the entity is function.
    global block_name # name of the block that is being compiled
    begin_block_quad = [] # begin_block quad for the block_name block
    for i in range(0,len(quads)):
        temp_quad = quads[i]
        if block_name == temp_quad[2]:
            begin_block_quad = temp_quad
            break
    for j in range(begin_block_quad[0],len(quads)):
        temp_quads = quads[j]
        if isfunction is True and temp_quads[1] == "retv":
            return
        elif isfunction is False and temp_quads[1] == "retv":
            print("ERROR: Procedures must not contain return statements in " + block_name)
            exit()
    if isfunction is True:
        print("ERROR: Return statement missing in function " + block_name)
        exit()
            
#######################################
# Check if there are return statements in the main part of the code (Semantic Analysis)
#######################################
def checkReturnMain():
    global main_name # name of the main function
    begin_main_quad = [] # begin_block quad of main 
    for i in range(0,len(quads)):
        temp_quad = quads[i]
        if main_name == temp_quad[2]:
            begin_main_quad = temp_quad
            break
    for j in range(begin_main_quad[0],len(quads)):
        temp_quad = quads[j]
        if temp_quad[1] == "retv":
            print("ERROR: Return statements are not allowed outside function range(main part of the code).")
            exit()

#######################################
# Check if variables are used in variable-based operations, if functions are used in function-based operations (Semantic Analysis)
#######################################
def checkEntityUsage():
    global block_name # name of the block that is being compiled
    begin_block_quad = [] # begin_block quad of block_name block
    for i in range(0,len(quads)):
        temp_quad = quads[i]
        if block_name == temp_quad[2]:
            begin_block_quad = temp_quad
            break
    for j in range(begin_block_quad[0],len(quads)):
        temp_quad = quads[j]
        if temp_quad[1] == "+" or temp_quad[1] == "-" or temp_quad[1] == "*" or temp_quad[1] == "/":
            if str(temp_quad[2]).isdigit():
                if str(temp_quad[3]).isdigit():
                    lastEntity,nestinglevel = searchEntity(temp_quad[4])
                    if lastEntity.entitytype == "variable":
                        continue
                    else:
                        print("ERROR: Only variables and numbers are allowed in arithmetic operations (" + block_name + ") block.")
                        exit()
                else:
                    nextEntity,nestinglevel = searchEntity(temp_quad[3])
                    if nextEntity.entitytype == "variable":
                        lastEntity,nestinglevel = searchEntity(temp_quad[4])
                        if lastEntity.entitytype == "variable":
                            continue
                        else:
                            print("ERROR: Only variables and numbers are allowed in arithmetic operations (" + block_name + ") block.")
                            exit()
                    else:
                        print("ERROR: Only variables and numbers are allowed in arithmetic operations (" + block_name + ") block.")
                        exit()
            else:           
                entity,nestinglevel = searchEntity(temp_quad[2])
                if entity.entitytype == "variable":
                    if temp_quad[3].isdigit():
                        lastEntity ,nestinglevel= searchEntity(temp_quad[4])
                        if lastEntity.entitytype == "variable":
                            continue
                        else:
                            print("ERROR: Only variables and numbers are allowed in arithmetic operations(" + block_name + ") block.")
                            exit()
                    else:
                        nextEntity,nestinglevel = searchEntity(temp_quad[3])
                        if nextEntity.entitytype == "variable":
                            lastEntity,nestinglevel = searchEntity(temp_quad[4])
                            if lastEntity.entitytype == "variable":
                                continue
                            else:
                                print("ERROR: Only variables and numbers are allowed in arithmetic operations(" + block_name + ") block.")
                                exit()
                        else:
                            print("ERROR: Only variables and numbers are allowed in arithmetic operations(" + block_name + ") block.")
                            exit()
                else:
                    print("ERROR: Only variables and numbers are allowed in arithmetic operations(" + block_name + ") block.")
                    exit()
        elif temp_quad[1] == "<" or temp_quad[1] == ">" or temp_quad[1] == "<=" or temp_quad[1] == ">=" or temp_quad[1] == "=" or temp_quad[1] == "<>":
            if str(temp_quad[2]).isdigit():
                if str(temp_quad[3]).isdigit():
                    continue
                else: 
                    nextEntity,nestinglevel = searchEntity(temp_quad[3])
                    if nextEntity.entitytype == "variable":
                        continue 
                    else:
                        print("ERROR: Only variables and numbers are allowed in relational operations(" + block_name + ") block.")
                        exit()
            else:
                entity,nestinglevel = searchEntity(temp_quad[2])
                if entity.entitytype == "variable":
                    if str(temp_quad[3]).isdigit():
                        continue
                    else:
                        nextEntity,nestinglevel = searchEntity(temp_quad[3])
                        if nextEntity.entitytype == "variable":
                            continue 
                        else:
                            print("ERROR: Only variables and numbers are allowed in relational operations(" + block_name + ") block.")
                            exit()
                else:
                    print("ERROR: Only variables and numbers are allowed in relational operations(" + block_name + ") block.")
                    exit() 
        elif temp_quad[1] == ":=":
            if str(temp_quad[2]).isdigit():
                lastEntity,nestinglevel = searchEntity(temp_quad[4])
                if lastEntity.entitytype == "variable":
                    continue
                else:
                    print("ERROR: Only variables are allowed in assignments(" + block_name + ") block.")
                    exit()
            else:
                entity,nestinglevel = searchEntity(temp_quad[2])
                if entity.entitytype == "variable":
                    lastEntity,nestinglevel = searchEntity(temp_quad[4])
                    if lastEntity.entitytype == "variable":
                        continue
                    else:
                        print("ERROR: Only variables are allowed in assignments(" + block_name + ") block.")
                        exit()
                else:
                    print("ERROR: Only variables are allowed in assignments(" + block_name + ") block.")
                    exit()
        elif temp_quad[1] == "par":
            if str(temp_quad[2]).isdigit():
                continue
            else:
                entity,nestinglevel = searchEntity(temp_quad[2])
                if entity.entitytype == "variable":
                    continue
                else:
                    print("ERROR: Only variables and numbers are allowed in function arguments(" + block_name + ") block.")
                    exit()
        elif temp_quad[1] == "call":
            entity,nestinglevel = searchEntity(temp_quad[2])
            if entity.entitytype == "function" or entity.entitytype == "procedure":
                continue
            else:
                print("ERROR: Only functions/procedures are allowed to be called not variables(" + block_name + ") block.")
                exit()
        elif temp_quad[1] == "out" or temp_quad[1] == "inp" or temp_quad[1] == "retv":
            if str(temp_quad[2]).isdigit():
                continue
            else:
                entity,nestinglevel = searchEntity(temp_quad[2])
                if entity.entitytype == "variable":
                    continue
                else:
                    print("ERROR: Only variables and numbers are allowed in print/input/return statements (" + block_name + ") block.")
                    exit()

#######################################
# Calculate the framelength of Main part of the code and return it (MIPS Assembly Code Generation)
#######################################
def calculateMainFramelength():
    global lastscope # current scope
    returnFramelength = 12
    for entity in lastscope.entity:
        if entity.entitytype == "variable":
            returnFramelength += 4
    return returnFramelength

#######################################
# Find the address of a non-local variable and store it to $t0 (MIPS Assembly Code Generation)
#######################################
def gnlvcode(v):
    global lastscope # current scope
    MIPS_assembly_commands.append("\tlw $t0,-4($sp)")
    entity,nestinglevel = searchEntity(v)
    nestingleveldifference = lastscope.nestinglevel - lastscope.nestinglevel
    for i in range(0,nestingleveldifference - 1):
        MIPS_assembly_commands.append("\tlw $t0,-4($t0)")
    MIPS_assembly_commands.append("\taddi $t0,$t0,-" + str(entity.offset))

#######################################
# Load variable v to register r (MIPS Assembly Code Generation)
#######################################
def loadvr(v,r):
    global lastscope # current scope
    if str(v).isdigit():
        MIPS_assembly_commands.append("\tli " + r + "," + str(v))
    else:
        entity,nestinglevel = searchEntity(v)
        if nestinglevel == 0:
            MIPS_assembly_commands.append("\tlw " + r + ",-" + str(entity.offset) + "($s0)")
        elif nestinglevel == lastscope.nestinglevel or entity.parmode == "in" and entity.parmode != "inout":
            MIPS_assembly_commands.append("\tlw " + r + ",-" + str(entity.offset) + "($sp)")
        elif nestinglevel == lastscope.nestinglevel and entity.parmode == "inout":
            MIPS_assembly_commands.append("\tlw $t0" +  ",-" + str(entity.offset) + "($sp)")
            MIPS_assembly_commands.append("\tlw " + r + ",($t0)")
        elif lastscope.nestinglevel > nestinglevel or entity.parmode == "in" and entity.parmode != "inout":
            gnlvcode(v)
            MIPS_assembly_commands.append("\tlw " + r + ",($t0)")
        elif lastscope.nestinglevel > nestinglevel and entity.parmode == "inout":
            gnlvcode(v)
            MIPS_assembly_commands.append("\tlw $t0,($t0)")
            MIPS_assembly_commands.append("\tlw " + r + ",($t0)")  

#######################################
# Store register r to variable v (MIPS Assembly Code Generation)
#######################################
def storerv(v,r):
    global lastscope # current scope
    entity,nestinglevel = searchEntity(v)
    if nestinglevel == 0:
        MIPS_assembly_commands.append("\tsw " + r + ",-" + str(entity.offset) + "($s0)")
    elif nestinglevel == lastscope.nestinglevel or entity.parmode == "in" and entity.parmode != "inout":
        MIPS_assembly_commands.append("\tsw " + r + ",-" + str(entity.offset) + "($sp)")
    elif nestinglevel == lastscope.nestinglevel and entity.parmode == "inout":
        MIPS_assembly_commands.append("\tlw $t0,-" + str(entity.offset) + "($sp)")
        MIPS_assembly_commands.append("\tsw " + r + ",($t0)")
    elif lastscope.nestinglevel > nestinglevel or entity.parmode == "in" and entity.parmode != "inout":
        gnlvcode(v)
        MIPS_assembly_commands.append("\tsw " + r + ",($t0)")
    elif lastscope.nestinglevel > nestinglevel and entity.parmode == "inout":
        gnlvcode(v)
        MIPS_assembly_commands.append("\tlw $t0,($t0)")
        MIPS_assembly_commands.append("\tsw " + r + ",($t0)")

#######################################
# Use Intermediate Code and Symbols Array to generate MIPS Assembly commands (MIPS Assembly Code Generation)
#######################################
def MIPSCodeGenerator(blockName):
    global block_names # blocks that already being compiled
    global lastscope # current scope
    global main_name # name of the main function of the program
    commandDictionary = {"<":"blt","<=":"ble","=":"beq","<>":"bne",">":"bgt",">=":"bge","+":"add","-":"sub","*":"mul","/":"div"}
    numPar = 0 # number of par quads
    firstCall = 0 # varible to parse called_functions array
    if blockName in block_names:
        print("ERROR: Functions must not have the same name (" + block_name + " is defined multiple times).")
        exit()
    block_names.append(blockName)
    begin_block_quad = []
    for i in range(0,len(quads)):
        temp_quad = quads[i]
        if blockName == temp_quad[2]:
            begin_block_quad = temp_quad
            break
    for j in range(begin_block_quad[0],len(quads)):
        temp_quad = quads[j]
        MIPS_assembly_commands.append("L_" + str(temp_quad[0]) + ":")
        if temp_quad[1] == "jump":
            MIPS_assembly_commands.append("\tb L_" + str(temp_quad[4]))
        elif temp_quad[1] == "<" or temp_quad[1] == "<=" or temp_quad[1] == "=" or temp_quad[1] == "<>" or temp_quad[1] == ">" or temp_quad[1] == ">=":
            loadvr(temp_quad[2],"$t1")
            loadvr(temp_quad[3],"$t2")
            MIPS_assembly_commands.append("\t"+ commandDictionary.get(temp_quad[1]) + " $t1,$t2,L_" + str(temp_quad[4]))
        elif temp_quad[1] == ":=":
            loadvr(temp_quad[2],"$t1")
            storerv(temp_quad[4],"$t1")
        elif temp_quad[1] == "+" or temp_quad[1] == "-" or temp_quad[1] == "*" or temp_quad[1] == "/":
            loadvr(temp_quad[2],"$t1")
            loadvr(temp_quad[3],"$t2")
            MIPS_assembly_commands.append("\t" + commandDictionary.get(temp_quad[1]) + " $t1,$t1,$t2")
            storerv(temp_quad[4],"$t1")
        elif temp_quad[1] == "out":
            MIPS_assembly_commands.append("\tli $v0,1")
            loadvr(temp_quad[2],"$a0")
            MIPS_assembly_commands.append("\tsyscall")
        elif temp_quad[1] == "inp":
            MIPS_assembly_commands.append("\tli $v0,5")
            MIPS_assembly_commands.append("\tsyscall")
            storerv(temp_quad[2],"$v0")
        elif temp_quad[1] == "retv":
            loadvr(temp_quad[2],"$t1")
            MIPS_assembly_commands.append("\tlw $t0,-8($sp)")
            MIPS_assembly_commands.append("\tsw $t1,($t0)")
        elif temp_quad[1] == "par":
            if numPar == 0:
                entity,nestinglevel = searchEntity(called_functions[firstCall])
                MIPS_assembly_commands.append("\taddi $fp,$sp," + str(entity.framelength))
            if temp_quad[3] == "CV":
                loadvr(temp_quad[2],"$t0")
                MIPS_assembly_commands.append("\tsw $t0,-" + str(12 + 4*numPar) + "($fp)")
                numPar += 1
            elif temp_quad[3] == "REF":
                variableEntity,variableNestinglevel = searchEntity(temp_quad[2])
                functionEntity,functionNestinglevel = searchEntity(called_functions[firstCall])
                if variableNestinglevel == functionNestinglevel:
                    if variableEntity.parmode != "inout":
                        MIPS_assembly_commands.append("\taddi $t0,$sp,-" + str(variableEntity.offset))
                        MIPS_assembly_commands.append("\tsw $t0,-" + str(12+4*numPar) + "($fp)")
                    elif variableEntity.parmode == "inout":
                        MIPS_assembly_commands.append("\tlw $t0,-" + variableEntity.offset + "($sp)")
                        MIPS_assembly_commands.append("\tsw $t0,-(" + str(12+4*numPar) + ")($fp)")
                else:
                    if variableEntity.parmode != "inout":
                        gnlvcode(temp_quad[2])
                        MIPS_assembly_commands.append("\tsw $t0,-" + str(12+4*numPar) + "($fp)")
                    elif variableEntity.parmode == "inout":
                        gnlvcode(temp_quad[2])
                        MIPS_assembly_commands.append("\tlw $t0,($t0)")
                        MIPS_assembly_commands.append("\tsw $t0,-" + str(12+4*numPar) + "($fp)")
                numPar += 1
                firstCall += 1
            elif temp_quad[3] == "RET":
                variableEntity,variableNestinglevel = searchEntity(temp_quad[2])
                MIPS_assembly_commands.append("\taddi $t0,$sp,-" + str(variableEntity.offset))
                MIPS_assembly_commands.append("\tsw $t0,-8($fp)")
        elif temp_quad[1] == "call":
            calledFunctionEntity,calledFunctionNestinglevel = searchEntity(temp_quad[2])
            if lastscope.nestinglevel == 0:
                MIPS_assembly_commands.append("\tsw $sp,-4($fp)")
            else:
                callerFunctionEntity,callerFunctionNestinglevel = searchEntity(blockName)
                if callerFunctionEntity == calledFunctionNestinglevel:
                    MIPS_assembly_commands.append("\tlw $t0,-4($sp)")
                    MIPS_assembly_commands.append("\tsw $t0,-4($fp)")
                else:
                    MIPS_assembly_commands.append("\tsw $sp,-4($fp)")
            MIPS_assembly_commands.append("\taddi $sp,$sp," + str(calledFunctionEntity.framelength))
            MIPS_assembly_commands.append("\tjal " + temp_quad[2])
            MIPS_assembly_commands.append("\taddi $sp,$sp,-" + str(calledFunctionEntity.framelength))
        elif temp_quad[1] == "begin_block" and temp_quad[2] != main_name:
            MIPS_assembly_commands.append("\tsw $ra,($sp)")
        elif temp_quad[1] == "end_block" and temp_quad[2] != main_name:
            MIPS_assembly_commands.append("\tlw $ra,($sp)")
            MIPS_assembly_commands.append("\tjr $ra")
        elif temp_quad[1] == "begin_block" and temp_quad[2] == main_name:
            mainFramelength = calculateMainFramelength()
            MIPS_assembly_commands.append("L_main:")
            MIPS_assembly_commands.append("\taddi $sp,$sp," + str(mainFramelength))
            MIPS_assembly_commands.append("\tmove $s0,$sp")
        elif temp_quad[1] == "end_block" and temp_quad[2] == main_name:
            MIPS_assembly_commands.append("\tli $v0,10")
            MIPS_assembly_commands.append("\tsyscall")

#######################################
# Lexical Analysis implementation (Lexical Analysis)
#######################################
def lex(filename, position, lineNo):
    f = open(filename,'r') # open .ci file
    keywords = ["program","if","switchcase","not","function","input","declare","else","forcase","and","procedure","print","while","incase","or","call","case","return","default","in","inout"]
    token = '' # initialize return token
    f.seek(position)
    c = f.read(1)
    token += c
    if c.isalpha():
        cnew = f.read(1)
        while(cnew.isalpha() or cnew.isdigit()):
            token += cnew
            cnew = f.read(1)
        if len(token) <= 30 and token in keywords:
            pos = f.tell()
            return [token,"keyword",lineNo,pos-1]
        elif len(token) <= 30:
            pos = f.tell()
            return [token,"identifier",lineNo,pos-1]
        else:
            print("ERROR: Identifier too long in line " + str(lineNo) + "\n")
            exit()
    elif c.isdigit():
        cnew = f.read(1)
        if cnew.isalpha():
            print("ERROR: Found identifier that starts with number in line " + str(lineNo) + "\n")
            exit()
        while(cnew.isdigit()):
            token += cnew
            cnew = f.read(1)
            if cnew.isalpha():
                print("ERROR: Found identifier that starts with number in line " + str(lineNo) + "\n")
                exit()
        if ((int(token)) <= ((2**32) - 1)):
            pos = f.tell()
            return [token,"number",lineNo,pos-1]
        else:
            print("ERROR: Arithmetic overflow in line " + str(lineNo) + "\n")
            exit()
    elif c == '+' or c == '-':
        pos = f.tell()
        return[token,"addOperator",lineNo,pos]
    elif c == '*' or c == '/':
        pos = f.tell()
        return[token,"mulOperator",lineNo,pos]
    elif c == '{' or c == '}' or c == '(' or c == ')' or c == '[' or c == ']':
        pos = f.tell()
        return[token,"groupSymbol",lineNo,pos]
    elif c == ',' or c == ';':
        pos = f.tell()
        return[token,"delimiter",lineNo,pos]
    elif c == ':':
        cnew = f.read(1)
        if cnew == '=':
            pos = f.tell()
            token += cnew
            return [token,"assignment",lineNo,pos]
        else:
            print("ERROR: Not found '=' after ':' in line " + str(lineNo) + "\n")
            return
    elif c == '<':
        cnew = f.read(1)
        if cnew == '=':
            token += cnew
            pos = f.tell()
            return [token,"relOperator",lineNo,pos]
        elif cnew == '>':
            token += cnew
            pos = f.tell()
            return [token,"relOperator",lineNo,pos]
        else:
            pos = f.tell()
            return [token,"relOperator",lineNo,pos-1]
    elif c == '>':
        cnew = f.read(1)
        if cnew == '=':
            token += cnew
            pos = f.tell()
            return [token,"relOperator",lineNo,pos]
        else:
            pos = f.tell()
            return [token,"relOperator",lineNo,pos-1]
    elif c == "=":
        pos = f.tell()
        return [token,"relOperator",lineNo,pos]
    elif c == ".":
        pos = f.tell()
        return[token,"endProgram",lineNo,pos]
    elif c == "#":
        cnew = f.read(1)
        while(cnew != '#'):
            cnew = f.read(1)
            if cnew == '.':
                print("ERROR: End Of File reached and comment section is not closed in line " + str(lineNo) + "\n")
                exit()
            elif cnew == '#':
                pos = f.tell()
                return lex(fileName,pos,lineNo)
            elif cnew == '\n':
                lineNo = lineNo + 1
            elif cnew == '':
                print("ERROR: End Of File reached and comment section is not closed in line " + str(lineNo) + "\n")
                exit()
    elif c == '\t':
        pos = f.tell()
        return lex(fileName,pos,lineNo) 
    elif c == '\n':
        pos = f.tell()
        lineNo = lineNo + 1
        return lex(fileName,pos,lineNo)
    elif c == ' ':
        pos = f.tell()
        return lex(fileName,pos,lineNo)

#######################################
# Get id of the next quad (Intermediate Code)
#######################################
def nextquad():
    if not quads:
        return 0
    else:
        prev_quad = quads[-1]
        temp = prev_quad[0]
        temp += 1
        return temp

#######################################
# Generate next quad and find block name (Intermediate Code)
#######################################
def genquad(op,x,y,z):
    global lastscope # current scope
    global block_name # name of the block that is being compiled
    quad_id = nextquad()
    quads.append([quad_id,op,x,y,z])
    if lastscope.previousscope is not None:
        if op == "begin_block":
            lastscope.previousscope.entity[-1].startquad = quad_id
            block_name = x
    else:
        block_name = x
  
#######################################
# Create new temporary variable(Intermediate Code) and enters it to Symbols Array (Symbols Array)
#######################################
def newTemp():
    if not temps:
        temps.append("T_0")
        addentity("T_0","variable", None, None, None)
        return "T_0"
    else:
        numberoftemps = len(temps) - 1
        numberoftemps +=  1
        temps.append("T_" + str(numberoftemps))
        addentity("T_" + str(numberoftemps),"variable",None,None,None)
        return ("T_" + str(numberoftemps))

#######################################
# Create empty list (Intermediate Code)
#######################################
def emptylist():
    return []

#######################################
# Create list with one object in it (Intermediate Code)
#######################################
def makelist(x):
    return [x]

#######################################
# Merge two lists (Intermediate Code)
#######################################
def mergelist(list1,list2):
    merged_list = []
    for i in list1:
        merged_list.append(i)
    for j in list2:
        merged_list.append(j)
    return merged_list

#######################################
# Add element z in the last position of the quads that are in list (Intermediate Code)
#######################################
def backpatch(list,z):
    for i in list:
        quad = quads[i]
        del(quad[-1])
        quad.append(z)
        quads[i] = quad

#######################################
# Add sign in the beginning of expressions (Syntax Analysis)
#######################################
def optionalSign(fileName,token):
    if token[1] == "addOperator":
        token = lex(fileName,token[3],token[2])
    return token

#######################################
# Find if function syntax is correct after an identifier (Syntax Analysis)
#######################################
def idtail(fileName,token,name,PARplace):
    if token[0] == '(':
        token = lex(fileName,token[3],token[2])
        token = actualparlist(fileName,token,name,PARplace)
        if token[0] == ')':
            token = lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
            exit()
    return token

#######################################
# Find numbers, variable identifiers or function identifiers (Syntax Analysis)
#######################################
def factor(fileName,token,Fplace):
    Eplace = [] # variables where the expressions' result will be stored.
    if token[1] == "number":
        Fplace.append(str(token[0]))
        token = lex(fileName,token[3],token[2])
    elif token[0] == '(':
        token = lex(fileName,token[3],token[2])
        token = expression(fileName,token,Eplace)
        if token[0] == ')':
            Fplace.append(Eplace)
            token = lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
            exit()
    elif token[1] == "identifier":
        PARplace = []
        name = token[0]
        token = lex(fileName,token[3],token[2])
        token = idtail(fileName,token,name,PARplace)
        if PARplace:
            Fplace.append(PARplace[0])
        else:
            Fplace.append(name)
    else:
        print("ERROR: Expected number, identifier or '(' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Find multiply and division expressions (Syntax Analysis)
#######################################
def term(fileName,token,Tplace):
    F1place = [] # variables where the factor's result will be stored
    token = factor(fileName,token,F1place)
    while token[1] == "mulOperator":
        op = token[0]
        F2place = [] # variables where the factor's result will be stored
        token = lex(fileName,token[3],token[2])
        token = factor(fileName,token,F2place)
        w = newTemp()
        genquad(op,F1place[0],F2place[0],w)
        F1place = [w]
    Tplace.append(F1place)
    return token

#######################################
# Find addition and subtraction expressions (Syntax Analysis)
#######################################
def expression(fileName,token,Eplace):
    T1place = [] # variables where the token's result will be stored
    possiblesign = token[0] # symbol in the beginning of expression probably '-'
    token = optionalSign(fileName,token)
    token = term(fileName,token,T1place)
    if possiblesign == "-":
        genquad(possiblesign,"0",T1place[0][0],T1place[0][0]) 
    while token[1] == "addOperator":
        op = token[0]
        T2place = [] # variables where the token's result will be stored
        token = lex(fileName,token[3],token[2])
        token = term(fileName,token,T2place)
        w = newTemp()
        genquad(op,T1place[0][0],T2place[0][0],w)
        T1place = [[w]]
    Eplace.append(T1place)
    return token

#######################################
# Find boolean expressions (Syntax Analysis)
#######################################
def boolfactor(fileName,token,Rtrue,Rfalse):
    if token[0] == "not":
        Btrue = [] # quads that we will branch if the expression is True
        Bfalse = [] # quads that we will branch if the expression is False
        token = lex(fileName,token[3],token[2])
        if token[0] == '[':
            token = lex(fileName,token[3],token[2])
            token = condition(fileName,token,Btrue,Bfalse)
            if token[0] == ']':
                token = lex(fileName,token[3],token[2])
                for i in Btrue:
                    Rfalse.append(i)
                for j in Bfalse:
                    Rtrue.append(j)
            else:
                print("ERROR: Expected ']' in line " + str(token[2]) + "\n")
                exit() 
        else:
            print("ERROR: Expected '[' in line " + str(token[2]) + "\n")
            exit()
    elif token[0] == '[':
        Btrue = [] # quads that we will branch if the expression is True
        Bfalse = [] # quads that we will branch if the expression is False
        token = lex(fileName,token[3],token[2])
        token = condition(fileName,token,Btrue,Bfalse)
        for i in Btrue:
            Rtrue.append(i)
        for j in Bfalse:
            Rfalse.append(j)
        if token[0] == ']':
            token = lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected ']' in line " + str(token[2]) + "\n")
            exit()
    else:
        E1place = [] # variables where the expressions' result will be stored.
        E2place = [] # variables where the expressions' result will be stored.
        token = expression(fileName,token,E1place)
        if token[1] == "relOperator":
            relop = token[0]
            token = lex(fileName,token[3],token[2])
            token = expression(fileName,token,E2place)
            Rtrue.append(makelist(nextquad())[0])
            genquad(relop,E1place[0][0][0],E2place[0][0][0],"_")
            Rfalse.append(makelist(nextquad())[0])
            genquad("jump","_","_","_")
    return token

#######################################
# Find 'and' boolean expressions (Syntax Analysis)
####################################### 
def boolterm(fileName,token,Qtrue,Qfalse):
    R1true = [] # quads that we will branch if the expression is True
    R1false = [] # quads that we will branch if the expression is False
    R2true = [] # quads that we will branch if the expression is True
    R2false = [] # quads that we will branch if the expression is False
    token = boolfactor(fileName,token,R1true,R1false)
    for i in R1true:
        Qtrue.append(i)
    for j in R1false:
        Qfalse.append(j)
    while token[0] == "and":
        backpatch(Qtrue,nextquad())
        Qtrue.clear()
        token = lex(fileName,token[3],token[2])
        token = boolfactor(fileName,token,R2true,R2false)
        merged = mergelist(Qfalse,R2false)
        Qfalse.clear()
        for i in merged:
            Qfalse.append(i)
        for j in R2true:
            Qtrue.append(j)
    return token

#######################################
# Find 'or' expressions (Syntax Analysis)
#######################################
def condition(fileName,token,Btrue,Bfalse):
    Q1true = [] # quads that we will branch if the expression is True
    Q1false = [] # quads that we will branch if the expression is False
    Q2true = [] # quads that we will branch if the expression is True
    Q2false = [] # quads that we will branch if the expression is False
    token = boolterm(fileName,token,Q1true,Q1false)
    for i in Q1true:
        Btrue.append(i) 
    for j in Q1false:
        Bfalse.append(j)
    while token[0] == "or":
        backpatch(Bfalse,nextquad())
        Bfalse.clear()
        token = lex(fileName,token[3],token[2])
        token = boolterm(fileName,token,Q2true,Q2false)
        merged = mergelist(Btrue,Q2true)
        Btrue.clear()
        for i in merged:
            Btrue.append(i)
        for j in Q2false:
            Bfalse.append(j)
    return token

#######################################
# Find function/procedure expression parameters (Syntax Analysis)
#######################################
def actualparitem(fileName,token,parametersCV,parametersREF):
    Eplace = [] # variables where the expression's result will be stored
    if token[0] == "in":
        token = lex(fileName,token[3],token[2])
        token = expression(fileName,token,Eplace)
        for i in Eplace:
            parametersCV.append(i[0][0])
    elif token[0] == "inout":
        token = lex(fileName,token[3],token[2])
        if token[1] == "identifier":
            parametersREF.append(token[0])
            token = lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected identifier in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected 'in' or 'inout' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Find function/procedure parameters in function call (Syntax Analysis) and check if function/procedure agruments are in the correct order (Semantic Analysis)
#######################################
def actualparlist(fileName,token,name,PARplace):
    global isfunction # boolean variable that states if the block that is being compiled is a function
    global lastscope # current scope
    global block_name # name of the block that is being compiled
    parametersCV = [] # parameters that are Connected by Value
    parametersREF = [] # parameters that are Connected by Reference
    argumentsList = [] # list of arguments
    tempLastScope = lastscope
    token = actualparitem(fileName,token,parametersCV,parametersREF)
    for i in parametersCV:
        genquad("par",i,"CV","_")
        argumentsList.append("in")
    for j in parametersREF:
        genquad("par",j,"REF","_")
        argumentsList.append("inout")
    while token[0] == ',':
        parametersCV.clear()
        parametersREF.clear()
        token = lex(fileName,token[3],token[2])
        token = actualparitem(fileName,token,parametersCV,parametersREF)
        for i in parametersCV:
            genquad("par",i,"CV","_")
            argumentsList.append("in")
        for j in parametersREF:
            genquad("par",j,"REF","_")
            argumentsList.append("inout")
    if isfunction is True:
        w = newTemp()
        genquad("par",w,"RET","_")
        PARplace.append(w)
    genquad("call",name,"_","_")
    while tempLastScope is not None:
        for e in tempLastScope.entity:
            if e.name == name:
                called_functions.append(e.name)
                arguments = e.arguments
                if len(arguments) == len(argumentsList):
                    for i in range(0,len(arguments)):
                        if arguments[i].parmode != argumentsList[i]:
                            print("ERROR: Expected " + arguments[i].parmode + " argument but found " + argumentsList[i] + " while calling " + name + ".")
                            exit()
                else:
                    print("ERROR: Number of arguments not accurate while calling " + name + ".")
                    exit()
        tempLastScope = tempLastScope.previousscope
    return token

#######################################
# Input statement implementation (Syntax Analysis)
#######################################
def inputStat(fileName,token):
    if token[0] == '(':
        token = lex(fileName,token[3],token[2])
        if token[1] == "identifier":
            id = token[0]
            token = lex(fileName,token[3],token[2])
            if token[0] == ')':
                token = lex(fileName,token[3],token[2])
                genquad("inp",id,"_","_")
            else:
                print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
                exit()
        else:
            print("ERROR: Expected identifier in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Print statement implementation (Syntax Analysis)
#######################################
def printStat(fileName,token):
    Eplace = [] # variables where the expression's result will be stored
    if token[0] == '(':
        token = lex(fileName,token[3],token[2])
        token = expression(fileName,token,Eplace)
        if token[0] == ')':
            token = lex(fileName,token[3],token[2])
            genquad("out",Eplace[0][0][0],"_","_")
        else:
            print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Call statement implementation (Syntax Analysis) and check symbol array if explicit call command is called by procedure (Semantic Analysis)
#######################################
def callStat(fileName,token):
    global isfunction # boolean variable that states if the block that is being compiled is a function
    PARplace = [] # variable where the return result of a function is stored
    entity,nestinglevel = searchEntity(token[0])
    if entity.entitytype != "procedure":
        print("ERROR: Only procedures are allowed to be explicitly called not functions/variables.")
        exit()
    if token[1] == "identifier":
        functionName = token[0]
        token = lex(fileName,token[3],token[2])
        if token[0] == '(':
            token = lex(fileName,token[3],token[2])
            token = actualparlist(fileName,token,functionName,PARplace)
            if token[0] == ')':
                token = lex(fileName,token[3],token[2])
            else:
                print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
                exit()
        else:
            print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected identifier in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Return statement implementation (Syntax Analysis)
#######################################
def returnStat(fileName,token):
    Eplace = [] # variables where the expression's result will be stored
    if token[0] == '(':
        token = lex(fileName,token[3],token[2])
        token = expression(fileName,token,Eplace)
        if token[0] == ')':
            token = lex(fileName,token[3],token[2])
            genquad("retv",Eplace[0][0][0],"_","_")
        else:
            print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Incase statement implementation (Syntax Analysis)
#######################################
def incaseStat(fileName,token):
    Btrue = [] # labels where the code will branch if the condition is True
    Bfalse = [] # labels where the code will branch if the condition is False
    w = newTemp()
    p1Quad = nextquad()
    genquad(":=",1,"_",w)
    while token[0] == "case":
        Btrue.clear()
        Bfalse.clear()
        token = lex(fileName,token[3],token[2])
        if token[0] == '(':
            token = lex(fileName,token[3],token[2])
            token = condition(fileName,token,Btrue,Bfalse)
            if token[0] == ')':
                backpatch(Btrue,nextquad())
                genquad(":=",0,"_",w)
                token = lex(fileName,token[3],token[2])
                token = statements(fileName,token)
                backpatch(Bfalse,nextquad())
            else:
                print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
                exit()
        else:
            print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
            exit()
    genquad("=",w,0,p1Quad)
    return token

#######################################
# Forcase statement implementation (Syntax Analysis)
#######################################
def forcaseStat(fileName,token):
    Btrue = [] # labels where the code will branch if the condition is True
    Bfalse = [] # labels where the code will branch if the condition is False
    p1Quad = nextquad()
    while token[0] == "case":
        Btrue.clear()
        Bfalse.clear()
        token = lex(fileName,token[3],token[2])
        if token[0] == '(':
            token = lex(fileName,token[3],token[2])
            token = condition(fileName,token,Btrue,Bfalse)
            if token[0] == ')':
                backpatch(Btrue,nextquad())
                token = lex(fileName,token[3],token[2])
                token = statements(fileName,token)
                genquad("jump","_","_",p1Quad)
                backpatch(Bfalse,nextquad())
            else:
                print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
                exit()
        else:
            print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
            exit()
    if token[0] == "default":
        token = lex(fileName,token[3],token[2])
        token = statements(fileName,token)
    else:
        print("ERROR: Expected keyword 'default' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Switchcase statement implementation (Syntax Analysis)
#######################################
def switchcaseStat(fileName,token):
    Btrue = [] # labels where the code will branch if the condition is True
    Bfalse = [] # labels where the code will branch if the condition is False
    exitlist = emptylist()
    while token[0] == "case":
        Btrue.clear()
        Bfalse.clear()
        token = lex(fileName,token[3],token[2])
        if token[0] == '(':
            token = lex(fileName,token[3],token[2])
            token = condition(fileName,token,Btrue,Bfalse)
            if token[0] == ')':
                backpatch(Btrue,nextquad())
                token = lex(fileName,token[3],token[2])
                token = statements(fileName,token)
                e = makelist(nextquad())
                genquad("jump","_","_","_")
                exitlist = mergelist(exitlist,e)
                backpatch(Bfalse,nextquad())
            else:
                print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
                exit()
        else:
            print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
            exit()
    if token[0] == "default":
        token = lex(fileName,token[3],token[2])
        token = statements(fileName,token)
        backpatch(exitlist,nextquad())
    else:
        print("ERROR: Expected keyword 'default' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# While statement implementation (Syntax Analysis)
#######################################
def whileStat(fileName,token):
    Btrue = [] # labels where the code will branch if the condition is True
    Bfalse = [] # labels where the code will branch if the condition is False
    Bquad = nextquad()
    if token[0] == '(':
        token = lex(fileName,token[3],token[2])
        token = condition(fileName,token,Btrue,Bfalse)
        backpatch(Btrue,nextquad())
        if token[0] == ')':
            token = lex(fileName,token[3],token[2])
            token = statements(fileName,token)
            genquad("jump","_","_",str(Bquad))
            backpatch(Bfalse,nextquad())
        else:
            print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Else statement implementation (Syntax Analysis)
#######################################
def elsepart(fileName,token):
    if token[0] == "else":
        token = lex(fileName,token[3],token[2])
        token = statements(fileName,token)
    return token

#######################################
# If statement implementation (Syntax Analysis)
#######################################
def ifStat(fileName,token):
    Btrue = [] # labels where the code will branch if the condition is True
    Bfalse = [] # labels where the code will branch if the condition is False
    if token[0] == '(':
        token = lex(fileName,token[3],token[2])
        token = condition(fileName,token,Btrue,Bfalse)
        if token[0] == ')':
            backpatch(Btrue,nextquad())
            token = lex(fileName,token[3],token[2])
            token = statements(fileName,token)
            ifList = makelist(nextquad())
            genquad("jump","_","_","_")
            backpatch(Bfalse,nextquad())
            token = elsepart(fileName,token)
            backpatch(ifList,nextquad())
        else: 
            print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Assign statement implementation (Syntax Analysis)
#######################################
def assignStat(fileName,token,id):
    Eplace = [] # variables where the expression's result is stored
    if token[0] == ":=":
        token = lex(fileName,token[3],token[2])
        token = expression(fileName,token,Eplace)
        genquad(":=",Eplace[0][0][0],"_",id)
    else:
        print("ERROR: Expected ':=' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Select which statement is going to be implemented (Syntax Analysis)
#######################################
def statement(fileName,token):
    if token[1] == "identifier":
        id = token[0]
        token = lex(fileName,token[3],token[2])
        token = assignStat(fileName,token,id)
    elif token[0] == "if":
        token = lex(fileName,token[3],token[2])
        token = ifStat(fileName,token)
    elif token[0] == "while":
        token = lex(fileName,token[3],token[2])
        token = whileStat(fileName,token)
    elif token[0] == "switchcase":
        token = lex(fileName,token[3],token[2])
        token = switchcaseStat(fileName,token)
    elif token[0] == "forcase":
        token = lex(fileName,token[3],token[2])
        token = forcaseStat(fileName,token)
    elif token[0] == "incase":
        token = lex(fileName,token[3],token[2])
        token = incaseStat(fileName,token)
    elif token[0] == "call":
        token = lex(fileName,token[3],token[2])
        token = callStat(fileName,token)
    elif token[0] == "return":
        token = lex(fileName,token[3],token[2])
        token = returnStat(fileName,token)
    elif token[0] == "input":
        token = lex(fileName,token[3],token[2])
        token = inputStat(fileName,token)
    elif token[0] == "print":
        token = lex(fileName,token[3],token[2])
        token = printStat(fileName,token)
    return token

#######################################
# Statements' syntax structure implementation (Syntax Analysis)
#######################################
def statements(fileName,token):
    if token[0] == '{':
        token = lex(fileName,token[3],token[2])
        token = statement(fileName,token)
        if token[0] != ';':
            print("ERROR: Expected ';' in line " + str(token[2] - 1) + ".\n")
            exit()
        while token[0] == ';':
            token = lex(fileName,token[3],token[2])
            if token[0] == '}':
                break
            token = statement(fileName,token)
            if token[0] != ';':
                print("ERROR: Expected ';' in line " + str(token[2] - 1) + ".\n")
                exit()
        if token[0] == '}':
            token = lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected '}' in line " + str(token[2] - 1) + ".\n")
            exit()
    
        return token
    else:
        token = statement(fileName,token)
        if token[0] == ';':
            token = lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected ';' in line " + str(token[2]) + ".\n")
            exit()
        return token

#######################################
# Find if function/procedure parameters are connected by value or reference in function declaration (Syntax Analysis) and add arguments to Symbols Array (Symbols Array)
#######################################
def formalparitem(fileName,token):
    if token[0] == "in" or token[0] == "inout":
        parMode = token[0]
        token = lex(fileName,token[3],token[2])
        addargument(parMode,token[0])
        if token[1] == "identifier":
            token= lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected identifier in line " + str(token[2]) + "\n")
            exit()
    else:
        print("ERROR: Expected keywords 'in' or 'inout' in line " + str(token[2]) + "\n")
        exit()
    return token

#######################################
# Find function/procedure parameters in function declaration (Syntax Analysis)
#######################################
def formalparlist(fileName,token):
    token = formalparitem(fileName,token)
    while token[0] == ',':
        token = lex(fileName,token[3],token[2])
        token = formalparitem(fileName,token)
    return token

#######################################
# Subprograms syntax implementation (Syntax Analysis), add entity in the Symbols Array (Symbols Array), perform Semantic Analysis and MIPS Assembly Code Generation 
#######################################
def subprograms(fileName,token):
    global isfunction
    while(token[0] == "function" or token[0] == "procedure"):
        if token[0] == "function":
            isfunction = True
        else:
            isfunction = False
        token = lex(fileName,token[3],token[2])
        if isfunction == True:
            addentity(token[0],"function",None,None,None)
        else:
            addentity(token[0],"procedure",None,None,None)
        procedure_id = token[0]
        if token[1] == "identifier":
            token = lex(fileName,token[3],token[2])
            if(token[0] == '('):
                token = lex(fileName,token[3],token[2])
                token = formalparlist(fileName,token)
                if token[0] == ')':
                    token = lex(fileName,token[3],token[2])
                    token = block(fileName,token,procedure_id)
                    genquad("end_block",procedure_id,"_","_")
                    checkReturn()
                    checkEntityUsage()
                    MIPSCodeGenerator(procedure_id)
                    called_functions.clear()
                    deletescope(procedure_id)
                else:
                    print("ERROR: Expected ')' in line " + str(token[2]) + "\n")
                    exit()
            else:
                print("ERROR: Expected '(' in line " + str(token[2]) + "\n")
                exit()
        else:
            print("ERROR: Expected identifier in line " + str(token[2]) + "\n")
            exit()
    return token

#######################################
# Find the variables that are declared in the beginning of the block (Syntax Analysis) and add them to Symbols Array (Symbols Array)
#######################################
def varlist(fileName,token):
    if token[1] == "identifier":
        addentity(token[0],"variable",None,None,None)
        token = lex(fileName,token[3],token[2])
        while token[0] == ',':
            token = lex(fileName,token[3],token[2])
            if token[1] == "identifier":
                addentity(token[0],"variable",None,None,None)
                token = lex(fileName,token[3],token[2])
            else:
                print("ERROR: Expected identifier in line " + str(token[2]) + ",not keyword.\n")
                exit()
    return token

#######################################
# Variables declaration implementation (Syntax Analysis)
#######################################
def declarations(fileName,token):
    while token[0] == "declare":
        token = lex(fileName,token[3], token[2])
        token = varlist(fileName,token)
        if token[0] == ';':
            token = lex(fileName,token[3],token[2])
        else:
            print("ERROR: Expected ';' in line " + str(token[2] - 1) + "\n")
            exit()
    return token

#######################################
# Block syntax implementation (Syntax Analysis)
#######################################
def block(fileName,token,name):
    global lastscope # current scope
    createscope()
    token = declarations(fileName,token)
    token = subprograms(fileName,token)
    genquad("begin_block",name,"_","_")
    token = statements(fileName,token)
    return token

#######################################
# Program syntax implementation, also used as trigger to start compilation (Syntax Analysis) and perform Semantic Analysis and MIPS Assembly Code Generation
#######################################
def program(fileName, position, lineNo):
    global main_name # name of the main function
    global block_name # name of the block that is being compiled
    token = lex(fileName, position, lineNo)
    name = token[0]
    main_name = name
    block_name = name
    if(token[1] == "identifier"):
        token = lex(fileName, token[3], token[2])
        token = block(fileName,token,name)
        if token is None:
            print("ERROR: EOF reached and '.' symbol was not found.\n")
            exit() 
        elif token[0] == ".":
            genquad("halt","_","_","_")
            genquad("end_block",name,"_","_")
            checkReturnMain()
            checkEntityUsage()
            symbols_array.append("Scope:" + main_name)
            for i in lastscope.entity:
                if i.entitytype == "variable":
                    symbols_array.append("\t" + i.name + " " + str(i.offset))
                else:
                    symbols_array.append("\t" + i.name + " (" + str(i.framelength) + ")")
            MIPSCodeGenerator(name)
            return
            
    else:
        print("ERROR: Identifier to be used as program name expected in line " + str(lineNo) + ".\n")
        exit()

#######################################################################################################################################
#                                                       MAIN PART OF THE CODE
#######################################################################################################################################

#######################################
# Initializations
# 1.Get filename from terminal
# 2.Initialize arrays ,sets ,variables and Scope
#######################################

global lastscope
global block_name
global isfunction
global main_name
global block_names
lastscope = None # scope that is being compiled
block_name = "" # name of the block that is being compiled
isfunction = False # boolean variable to determine if a subprogram is a function
main_name = "" # name of the main block
block_names = [] # all the block names
called_functions = [] # subprograms that a scope is calling

fileName = sys.argv[1] # get the .ci filename
quads = [] # initialize array for quads (Intermediate Code)
temps = [] # initialize array for temporary variables (Intermediate Code)
token = [] # initialize array for tokens (Lexical and Syntax Analysis)
MIPS_assembly_commands = [] # initialize array for MIPS assembly commands
MIPS_assembly_commands.append("\tj L_main")
symbols_array = [] # initialize array for symbols arrays
variables = set([]) # initialize set for variable names
position = 0 # initialize position in .ci file
counter = 0 # initialize counter to count the number of blocks in the .ci file
line = 1 # initialize line number of the .ci file
int_fileName = fileName[0:-3] + ".int" # create .int file
asm_fileName = fileName[0:-3] + ".asm" # create .asm file
txt_fileName = fileName[0:-3] + "_symbols" + ".txt" # create .txt file

###############################################
# Execute compilation
# 1.Read first token and begin compilation
# 2.Open .int,.txt,.asm files
# 3.Write generated quads in the .int file 
# 4.Close .int file
############################################### 

token = lex(fileName,position,line)
if token[0] == "program":
    program(fileName,token[3],token[2]) # begin compilation
    f1 = open(int_fileName,"w")
    f3 = open(asm_fileName,"w")
    f4 = open(txt_fileName,"w")
else:
    print("ERROR: Expected keyword 'program' in line " + str(1) + ".\n")
f1.write("MARIOS IAKOVIDIS AM 4063 cs04063\nTHEOFILOS GEORGIOS PETSIOS AM 4158 cs04158\n\n")
for i in quads:
    for j in range(0,len(i)):
        f1.write(str(i[j]) + " ")
    f1.write("\n")
f1.close()

######################################################################################################################################
#                                               C EQUIVALENT OF INTERMEDIATE CODE
######################################################################################################################################
# Create .c file equivalent of the intermediate code 
#   1. Search for more than one blocks in quads list in order to find if there are functions/procedures in the code
#   2. Search the quads for variable names and save them in a Set
#   3. If there is not a function/procedure in the .ci file, open a file for writing the c commands
#   4. Print libraries, main, and variables definitions
#   5. Exclude begin_block, end_block and halt quads from the c code generation procedure
#   6. Generate c commands based on the quads and write them on the file
#   7. Write the quads next to the 
#   7. Close file
#######################################################################################################################################
for i in quads:
    if i[1] == "begin_block":
        counter += 1
    elif i[1] != "end_block":
        if i[1] != "halt":
            if str(i[2]).isalpha():
                variables.add(str(i[2]))
            if str(i[3]).isalpha():
                variables.add(str(i[3]))
            if str(i[4]).isalpha():
                variables.add(str(i[4]))

if counter == 1:
    c_fileName = fileName[0:-3] + ".c"
    f2 = open(c_fileName,"w")
    f2.write("// MARIOS IAKOVIDIS AM 4063 cs04063\n// THEOFILOS GEORGIOS PETSIOS AM 4158 cs04158\n")
    f2.write("#include <stdio.h>\n")
    f2.write("int main()\n")
    f2.write("{\n")
    f2.write("\tint " + ', '.join(variables) + ", " +  ', '.join(temps) +  ";\n")
    for i in quads:
        if i[1] != "begin_block":
            if i[1] != "end_block":
                if i[1] != "halt":
                    f2.write("\t")
                    f2.write("L_" + str(i[0]) + ": ")
                    if i[1] == "+" or i[1] == "-" or i[1] == "*" or i[1] == "/":
                        f2.write(str(i[4]) + " = " + str(i[2]) + str(" " + i[1] + " ") + str(i[3]) + "; ")
                    elif i[1] == "<" or i[1] == "<=" or i[1] == ">=" or i[1] == ">":
                        f2.write("if(" + str(i[2]) + str(i[1]) + str(i[3]) + ") goto L_" + str(i[4]) + "; ")
                    elif i[1] == "<>":
                        f2.write("if(" + str(i[2]) + " != " + str(i[3]) + ") goto L_" + str(i[4]) + "; ")
                    elif i[1] == "=":
                        f2.write("if(" + str(i[2]) + " == " + str(i[3]) + ") goto L_" + str(i[4]) + "; ")
                    elif i[1] == "jump":
                        f2.write("goto L_" + str(i[4]) + "; ")
                    elif i[1] == ":=":
                        f2.write(str(i[4]) + " = " + str(i[2]) + "; ")
                    elif i[1] == "out":
                        f2.write("printf(" + '"%d"' + ","+ str(i[2]) + "); ")
                    elif i[1] == "inp":
                        f2.write("scanf(" + '"%d"' + "," + "&" + str(i[2]) + "); ")
                    f2.write("// " + str(i) + "\n")
    f2.write("\treturn 0;\n")
    f2.write("}")
    f2.close()

####################################################################################################################################
# 1.Write MIPS Assembly Commands in the .asm file
# 2.Write Symbols Array in the .txt file
# 3.Close .int, .asm files
####################################################################################################################################
f3.write("# MARIOS IAKOVIDIS AM 4063 cs04063\n# THEOFILOS GEORGIOS PETSIOS AM 4158 cs04158\n\n")
for command in MIPS_assembly_commands:
    f3.write(command + "\n")

f4.write("MARIOS IAKOVIDIS AM 4063 cs04063\nTHEOFILOS GEORGIOS PETSIOS AM 4158 cs04158\n\n")
for symbol in symbols_array:
    f4.write(symbol + "\n")

f3.close()
f4.close()