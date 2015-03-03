class Logger:
    @staticmethod
    def error(file_name, line, exception, message):
        print("Error!")
        print("  File \"%s\", line %s" % (file_name, line))
        print("%s: %s" % (exception, message))
