SERVER_CXX_SRCS        := main.cpp server.cpp msg_parser.cpp
SERVER_INC			   := ./

X86_M32_CC 		:= 	gcc
X86_M32_CXX 	:= 	g++
X86_M32_LINK 	:= 	g++
X86_M32_CFLAGS  := -Wall -g -pthread -m32
X86_M32_CXXFLAGS  := -Wall -g -pthread
X86_M32_INC	    := $(SERVER_INC)
X86_M32_CSRCS   := 
X86_M32_CXXSRCS := $(SERVER_CXX_SRCS)
X86_M32_LDFLAGS := -lpthread
X86_M32_TARGET  :=  server.exe

ZYNQ_A9_CC 		:= 	arm-none-linux-gnueabi-gcc
ZYNQ_A9_CXX 	:= 	arm-none-linux-gnueabi-g++
ZYNQ_A9_LINK 	:= 	arm-none-linux-gnueabi-g++
ZYNQ_A9_CFLAGS  := -Wall -g -pthread -m32
ZYNQ_A9_CXXFLAGS  := -Wall -g -pthread
ZYNQ_A9_INC	    := $(SERVER_INC)
ZYNQ_A9_CSRCS   := 
ZYNQ_A9_CXXSRCS := $(SERVER_CXX_SRCS)
ZYNQ_A9_LDFLAGS := -lpthread
ZYNQ_A9_TARGET  :=  server.elf


## Common make
CC 			:= $(if $($BUILD)_CC, $($(BUILD)_CC), gcc)
CXX 		:= $(if $($BUILD)_CXX, $($(BUILD)_CXX), g++)
LINK 		:= $(if $($BUILD)_LINK, $($(BUILD)_LINK), g++)
V   		:= $(if $(VERBOSE), , @)

CXXSRCS := $($(BUILD)_CXXSRCS)
CSRCS 	 := $($(BUILD)_CSRCS)

CFLAGS   := $($(BUILD)_CFLAGS)
CXXFLAGS   := $($(BUILD)_CXXFLAGS)
LDFLAGS   := $($(BUILD)_LDFLAGS)

BUILD_DIR := build/$(BUILD)
INC	      := $(addprefix -I, $($(BUILD)_INC))
OBJS	  := $(patsubst %.cpp, $(BUILD_DIR)/%.o, \
				$(patsubst %.c, $(BUILD_DIR)/%.o, $(CXXSRCS) $(CSRCS)))

$($(BUILD)_TARGET) : $(BUILD_DIR) $(OBJS)
	$(V) $(LINK) $(CXXFLAGS) $(OBJS) -o $@ $(LDFLAGS)

$(BUILD_DIR)/%.o : %.c
	@ echo "\$$(CC)" $(CFLAGS) $(CXXFLAGS) "\$$(INC)" -c $(<F)
	$(V) $(CC) $(CFLAGS) $(INC) -c -o $@ $<

$(BUILD_DIR)/%.o : %.cpp 
	@ echo "\$$(CXX)" $(CFLAGS) $(CXXFLAGS) "\$$(INC)" -c $(<F)
	$(V) $(CXX) $(CXXFLAGS) $(INC) -c -o $@ $<

$(BUILD_DIR) :
	@ mkdir -p $(BUILD_DIR)

.PHONY : clean clean-all

clean : 
	rm -rf $(BUILD_DIR) $($(BUILD)_TARGET)


