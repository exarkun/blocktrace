from fcntl import ioctl
from sys import argv

from cffi import FFI

def main(name):
    ffi = FFI()
    ffi.cdef("""
static const int BLKTRACESETUP;
static const int BLKTRACESTART;
static const int BLKTRACESTOP;
static const int BLKTRACETEARDOWN;
static const int BLKTRACE_BDEV_SIZE;

struct blk_user_trace_setup {
    char name[BLKTRACE_BDEV_SIZE];  /* output */
    int act_mask;                   /* input */
    int buf_size;                   /* input */
    int buf_nr;                     /* input */
    int start_lba;
    int end_lba;
    int pid;
};
""")
    lib = ffi.verify(
        source="""
#include <linux/fs.h>
#include <linux/blktrace_api.h>
""")

    setup = ffi.new("struct blk_user_trace_setup")

    with open(name, "rb") as device:
        ioctl(device.fileno(), lib.BLKTRACESETUP, setup)


main(argv[1])
