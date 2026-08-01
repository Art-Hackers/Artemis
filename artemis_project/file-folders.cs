using System;
using System.IO;

class Program
{
    static void Main()
    {
        string currentPath = Directory.GetCurrentDirectory();
        
        Console.WriteLine($"Current Folder: {currentPath}");
        Console.WriteLine();
        
        string[] files = Directory.GetFiles(currentPath);
        string[] directories = Directory.GetDirectories(currentPath);
        
        Console.WriteLine("FILES:");
        if (files.Length == 0)
        {
            Console.WriteLine("  (No files)");
        }
        else
        {
            foreach (string file in files)
            {
                FileInfo info = new FileInfo(file);
                Console.WriteLine($"  {Path.GetFileName(file)} ({info.Length} bytes)");
            }
        }
        
        Console.WriteLine();
        Console.WriteLine("FOLDERS:");
        if (directories.Length == 0)
        {
            Console.WriteLine("  (No folders)");
        }
        else
        {
            foreach (string dir in directories)
            {
                Console.WriteLine($"  {Path.GetFileName(dir)}");
            }
        }
        
        Console.WriteLine();
        Console.WriteLine($"Total: {files.Length} files, {directories.Length} folders");
        Console.WriteLine();
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
    }
}
