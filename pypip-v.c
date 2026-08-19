#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int check_tool_version(const char *tool_name, const char *command) {
    char buffer[128];
    char output[512] = {0};
    int found_output = 0;

    FILE *pipe = popen(command, "r");
    if (!pipe) {
        printf("[ERROR] Failed to execute popen for %s.\n", tool_name);
        return 0;
    }

    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        // Safely append to output buffer
        size_t current_len = strlen(output);
        size_t space_left = sizeof(output) - current_len - 1;
        strncat(output, buffer, space_left);
        found_output = 1;
    }

    int status = pclose(pipe);

    if (status == 0 && found_output) {
        size_t len = strlen(output);
        if (len > 0 && output[len - 1] == '\n') {
            output[len - 1] = '\0';
        }
        printf("[SUCCESS] %s: %s\n", tool_name, output);
        return 1;
    }

    return 0;
}

int main() {
    printf("========================================\n");
    printf("       System Environment Check         \n");
    printf("========================================\n\n");

    // Check Python
    if (!check_tool_version("Python 3", "python3 --version 2>&1")) {
        if (!check_tool_version("Python", "python --version 2>&1")) {
            printf("[MISSING] Python is not installed or not in system PATH.\n");
        }
    }

    // Check Pip
    if (!check_tool_version("Pip 3", "pip3 --version 2>&1")) {
        if (!check_tool_version("Pip", "pip --version 2>&1")) {
            if (!check_tool_version("Pip (via python3 module)", "python3 -m pip --version 2>&1")) {
                printf("[MISSING] Pip is not installed or not in system PATH.\n");
            }
        }
    }

    // Check Git
    if (!check_tool_version("Git", "git --version 2>&1")) {
        printf("[MISSING] Git is not installed or not in system PATH.\n");
    }

    // Check GCC Compiler
    if (!check_tool_version("GCC", "gcc --version 2>&1")) {
        printf("[MISSING] GCC is not installed or not in system PATH.\n");
    }

    printf("\n========================================\n");
    printf("            Check Complete              \n");
    printf("========================================\n");

    return 0;
}
