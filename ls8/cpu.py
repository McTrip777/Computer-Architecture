"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.register = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 0xF4 
        self.branchTable = {}
        self.branchTable[0b10000010] = self.LDI 
        self.branchTable[0b01000111] = self.PRN 
        self.branchTable[0b00000001] = self.HLT 
        self.branchtable[0b01000101] = self.handleStackPush
        self.branchtable[0b01000110] = self.handleStackPop

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
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        ADD = 0b10100000
        SUB = 0b10100001
        MUL = 0b10100010
        DIV = 0b10100011
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        
        else:
            raise Exception("Unsupported ALU operation")

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
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
    
    def handleHLT(self):
        print('Process Ending.')
        sys.exit()

    def handleLDI(self, op1, op2):
        self.reg[op1] = op2

    def handlePRN(self, op1):
        print(self.reg[op1])

    def handleStackPush(self, op1):
        self.sp -= 1
        reg_value = self.reg[op1]
        self.ram[self.sp] = reg_value

    def handleStackPop(self, op1):
        ram_value = self.ram[self.sp]
        self.reg[op1] = ram_value
        self.sp += 1

    def run(self):
        """Run the CPU."""
        # self.register = [0] * 8
        # self.ram[00000000] * 256
        # self.pc = 0
        running = True


        while running:
            IR = self.ram[self.pc]
            
            op1 = self.ram_read(self.pc + 1)
            op2 = self.ram_read(self.pc + 2)
            instruction = (IR >> 6)
            alu_number = (IR >> 5)
            if alu_number:
                self.alu(IR, op1, op2)
            elif instruction == 2:
                self.branchtable[IR](op1, op2)
            elif instruction == 1:
                self.branchtable[IR](op1)
            elif instruction == 0:
                self.branchtable[IR]()
            else:
                if IR == HLT:
                    running = False

                self.pc += 1
                self.handleHLT()
            
            self.pc += 1 + instruction
