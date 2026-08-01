using System;
using System.IO;
using System.Linq;

class Program
{
    static void Main()
    {
        string currentPath = Directory.GetCurrentDirectory();
        
        Console.WriteLine($"Current Folder: {currentPath}");
        Console.WriteLine();
        
        var files = Directory.GetFiles(currentPath);
        var folders = Directory.GetDirectories(currentPath);
        
        Console.WriteLine($"FOLDERS ({folders.Length}):");
        if (folders.Length > 0)
        {
            foreach (string folder in folders)
            {
                DirectoryInfo dirInfo = new DirectoryInfo(folder);
                Console.WriteLine($"  {Path.GetFileName(folder)}");
                Console.WriteLine($"    Created: {dirInfo.CreationTime}");
                Console.WriteLine($"    Modified: {dirInfo.LastWriteTime}");
                Console.WriteLine();
            }
        }
        else
        {
            Console.WriteLine("  (No folders)");
            Console.WriteLine();
        }
        
        Console.WriteLine($"FILES ({files.Length}):");
        if (files.Length > 0)
        {
            foreach (string file in files)
            {
                FileInfo fileInfo = new FileInfo(file);
                Console.WriteLine($"  {Path.GetFileName(file)}");
                Console.WriteLine($"    Size: {fileInfo.Length} bytes");
                Console.WriteLine($"    Created: {fileInfo.CreationTime}");
                Console.WriteLine($"    Modified: {fileInfo.LastWriteTime}");
                Console.WriteLine();
            }
        }
        else
        {
            Console.WriteLine("  (No files)");
            Console.WriteLine();
        }
        
        long totalSize = files.Sum(f => new FileInfo(f).Length);
        Console.WriteLine($"SUMMARY:");
        Console.WriteLine($"  Total Folders: {folders.Length}");
        Console.WriteLine($"  Total Files: {files.Length}");
        Console.WriteLine($"  Total Size: {totalSize} bytes");
        
        Console.WriteLine();
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
    }
}
