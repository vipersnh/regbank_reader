#ifndef _UTILS_H_
#define _UTILS_H_

#define HOST            0
#define TARGET          1

typedef enum {
    ASSERT_NONFATAL,
    ASSERT_FATAL,
} assert_criticality_t;



#define assert(cond, crticality) {\
    if (!(cond)) { \
        assert_failed(__func__, __LINE__, crticality); \
    } \
}

void assert_failed(const char *func, int line, assert_criticality_t crt);

#endif
