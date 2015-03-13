# -*- coding: utf-8 -*-
class Logger:
    @staticmethod
    def warning(file_name, line, exception, message):
        Logger.log("Warning", file_name, line, exception, message)

    @staticmethod
    def error(file_name, line, exception, message):
        Logger.log("Error", file_name, line, exception, message)

    @staticmethod
    def log(log_type, file_name, line, exception, message):
        print("%s!" % (log_type))
        print("  File \"%s\", line %s" % (file_name, line))
        print("%s: %s" % (exception, message))
