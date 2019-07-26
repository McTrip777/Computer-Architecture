"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.fl = None
        self.sp = 0xF4 
        self.branchtable = {}
        self.lines = []
        self.branchtable[0b10000010] = self.handleLDI 
        self.branchtable[0b01000111] = self.handlePRN 
        self.branchtable[0b00000001] = self.handleHLT 
        self.branchtable[0b01000101] = self.handleStackPush
        self.branchtable[0b01000110] = self.handleStackPop
        self.branchtable[0b01010000] = self.handleCALL
        self.branchtable[0b00010001] = self.handleRET
        self.branchtable[0b01010100] = self.handleJMP
        self.branchtable[0b01010101] = self.handleJEQ
        self.branchtable[0b01010110] = self.handleJNE

    def load(self, fileName):
        """Load a program into memory."""

        address = 0

        lines = None
        try:
            lines = open(fileName).readlines()
        except FileNotFoundError:
            print(f"{fileName} Not Found.")
            sys.exit(2)

        for line in lines:
            if line[0].startswith('0') or line[0].startswith('1'):
                self.ram[address] = int(line[:8], 2)
                self.lines.append(line)
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        ADD = 0b10100000
        SUB = 0b10100001
        MUL = 0b10100010
        DIV = 0b10100011
        CMP = 0b10100111
        if op == ADD:
            self.register[reg_a] += self.register[reg_b]
        elif op == SUB:
            self.register[reg_a] -= self.register[reg_b]
        elif op == MUL:
            self.register[reg_a] *= self.register[reg_b]
        elif op == DIV:
            if not self.reg[reg_b]:
                print("Error: You are not allowed to divide a number by 0.")
                sys.exit()
            self.register[reg_a] /= self.register[reg_b]
        elif op == CMP:
            if self.register[reg_a] > self.register[reg_b]:
                self.fl = 0b00000010
            elif self.register[reg_a] < self.register[reg_b]:
                self.fl = 0b00000100
            else:
                self.fl = 0b00000001
 
        else:
            raise Exception("Unsupported ALU operation")
       
        self.pc += 3



    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]
 
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
 
    def handleHLT(self):
        print("HLT",'Process Ending.')
        sys.exit()
 
    def handleLDI(self, op1, op2):
        self.register[op1] = op2
        # print("LDI", op1, op2)
        self.pc += 3
 
    def handlePRN(self, op1):
        print(self.register[op1])
        self.pc += 2
 
    def handleStackPush(self, op1):
        self.sp -= 1
        reg_value = self.register[op1]
        self.ram[self.sp] = reg_value
        # print("StackPush", reg_value)
        self.pc += 2
 
    def handleStackPop(self, op1):
        ram_value = self.ram[self.sp]
        self.register[op1] = ram_value
        # print("StackPop", ram_value)
        self.sp += 1
 
        self.pc += 2
 
    def handleCALL(self, op1):
        return_address = self.pc + 2
        self.sp -= 1
        self.ram[self.sp] = return_address
        register_num = self.ram[self.pc + 1]
        subroutine_address = self.register[register_num]
        self.pc = subroutine_address
        # print("Call", subroutine_address)
 
    def handleRET(self):
        return_address = self.ram[self.sp]
        self.pc = return_address
        # print("RET", return_address)
 
    def handleJMP(self, op1):
        self.pc = self.register[op1]
        # print("JMP", self.pc)
 
    def handleJEQ(self, op1):
        if self.fl == 0b00000001:
            self.pc = self.register[op1]
        else:
            self.pc += 2
        # print("JEQ", self.pc)
 
    def handleJNE(self, op1):
        if (self.fl & 0b00000001) == 0b00000000:
            self.pc = self.register[op1]
        else:
            self.pc += 2
        # print("JNE", self.pc)

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            IR = self.ram[self.pc]
            # print("here", IR)
            op1 = self.ram_read(self.pc + 1)
            op2 = self.ram_read(self.pc + 2)
            instruction = (IR & 0b11000000) >> 6
            alu_number = (IR & 0b00100000) >> 5
            if alu_number == 1:
                self.alu(IR, op1, op2)
            elif instruction == 2:
                self.branchtable[IR](op1, op2)
            elif instruction == 1:
                self.branchtable[IR](op1)
            elif instruction == 0:
                self.branchtable[IR]()
            else:
                self.handleHLT()
            