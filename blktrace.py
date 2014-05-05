from fcntl import ioctl
from sys import argv
from errno import ENOENT

from cffi import FFI

def main(name):
    ffi = FFI()
    ffi.cdef("""
enum blktrace_cat {
    BLK_TC_WRITE,
    ...
};

static const int BLKTRACESETUP;
static const int BLKTRACESTART;
static const int BLKTRACESTOP;
static const int BLKTRACETEARDOWN;

static const int BLKTRACE_BDEV_SIZE;


struct blk_user_trace_setup {
    char name[...];      /* output */
    short act_mask;        /* input */
    int buf_size;        /* input */
    int buf_nr;          /* input */
    long start_lba;
    long end_lba;
    int pid;
};
""")
    lib = ffi.verify(
        source="""
#include <linux/fs.h>
#include <linux/blktrace_api.h>
""")

    setup = ffi.new("struct blk_user_trace_setup*")
    setup[0].start_lba = 0
    setup[0].end_lba = 0
    setup[0].pid = 0
    setup[0].name = b"\0" * lib.BLKTRACE_BDEV_SIZE
    setup[0].buf_size = 2 ** 16
    setup[0].buf_nr = 16
    setup[0].act_mask = lib.BLK_TC_WRITE
    with open(name, "rb") as device:
        while True:
            try:
                result = ioctl(device.fileno(), lib.BLKTRACESETUP, ffi.buffer(setup))
            except IOError as e:
                if e.errno == ENOENT:
                    print("Tearing down existing trace...")
                    ioctl(device.fileno(), lib.BLKTRACETEARDOWN)
                    continue
                raise
            else:
                name = ffi.buffer(setup[0].name)[:].rstrip(b"\x00")
                print("ioctl", result, name)
                break

        with open(b"/sys/kernel/debug/block/" + name + b"/trace0", "rb") as trace:
            while True:
                print repr(trace.read(1024))

    # TODO better TEARDOWN the trace someday!  Doesn't seem to work well to
    # leave it SETUP.


main(argv[1])
