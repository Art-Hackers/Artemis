// A normal test file
#include <stdio.h>
#include <stdlib.h>

int main() {
    char buffer[128];
  
    FILE *pipe = popen("python --version 2>&1", "r");
  
    if (!pipe) {
      
        printf("Failed to run command.\n");
      
        return 1;
    }

    if (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        printf("Detected Python Version: %s", buffer);
    } else {
        printf("Python is not installed or not in system PATH.\n");
    }

    pclose(pipe);
    return 0;
}
