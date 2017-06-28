import logging
import argparse
import os

__version__ = '0.1-dev'

#Usage: python Main.py --write --sprite zelda.spr --rom lttpromtobepatched.sfc #generates zelda_lttpromtobepatched.sfc
#       python Main.py --read --sprite zelda.spr --rom lttpromtobescanned.sfc #generates zelda.spr
#General rom patching logic copied from https://github.com/LLCoolDave/ALttPEntranceRandomizer

def write_byte(rom, address, value):
    rom[address] = value

def write_bytes(rom, startaddress, values):
    for i, value in enumerate(values):
        write_byte(rom, startaddress + i, value)

def patch_rom(args, rom, sprite, palette):
    write_bytes(rom, 0x80000, sprite)
    write_bytes(rom, 0xdd308, palette)

    # Frame advance logic copied from https://www.zeldix.net/t242-dummied-out-frame-control-in-zelda-lttp
    if args.frameadvance:
        rom[0x39] = 0xEA
        rom[0x3A] = 0xEA

    return rom

def create_sprite(args):
    logger = logging.getLogger('')

    logger.info('Creating sprite file.')

    rom = bytearray(open(args.rom, 'rb').read())

    sprite = bytearray(28672+90+6)

    #copy spritesheet
    for i in range(28672):
        sprite[i] = rom[0x80000+i]

    #copy palette
    for i in range(90):
        sprite[28672+i] = rom[0xdd308+i]

    #add padding
    for i in range(6):
        sprite[28672+90+i] = 0

    outfilename = '%s' % (args.sprite)

    with open('%s' % outfilename, 'wb') as outfile:
        outfile.write(sprite)

    logger.info('Done.')

    return sprite

def create_patched_rom(args):
    logger = logging.getLogger('')

    logger.info('Patching ROM.')

    spritesheet = bytearray(open(args.sprite, 'rb').read())

    rom = bytearray(open(args.rom, 'rb').read())

    sprite = bytearray(28672)

    palette = bytearray(90)

    for i in range(28672):
        sprite[i] = spritesheet[i]

    for i in range(90):
        palette[i] = spritesheet[28672+i]

    patched_rom = patch_rom(args, rom, sprite, palette)

    outfilename = '%s_%s' % (os.path.basename(args.sprite).replace(".spr",""), os.path.basename(args.rom))

    with open('%s' % outfilename, 'wb') as outfile:
        outfile.write(patched_rom)

    logger.info('Done.')

    return patched_rom

def main(args):
    if args.write:
        create_patched_rom(args)
        return

    if args.read:
        create_sprite(args)
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--loglevel', default='info', const='info', nargs='?', choices=['error', 'info', 'warning', 'debug'], help='Select level of logging for output.')
    parser.add_argument('--sprite', help='Path to a sprite sheet to use for Link. Needs to be in binary format and have a length of 0x7000 (28672) (sprite) followed by 0x5a (90) (palette) bytes.')
    parser.add_argument('--rom', help='Path to a lttp rom to be patched.')
    parser.add_argument('--write', help='Patches rom with provided sprite file', action='store_true')
    parser.add_argument('--read', help='Creates sprite file from provided rom', action='store_true')
    parser.add_argument('--frameadvance', help='Patches rom with the frame advance feature for sprite work (press L to freeze, R to advance a single frame, L to resume) (default: off)', action='store_true')
    args = parser.parse_args()

    if (args.read and args.write) or ((args.read != True) and (args.write != True)):
        input('Need to specify whether to read or write sprite. Please run with -h to see help for further information. \nPress Enter to exit.')
        exit(1)
    if args.rom is None:
        input('No rom specified. Please run with -h to see help for further information. \nPress Enter to exit.')
        exit(1)
    if args.sprite is None:
        input('No sprite specified. Please run with -h to see help for further information. \nPress Enter to exit.')
        exit(1)
    if not os.path.isfile(args.rom):
        input('Could not find valid rom for patching at path %s. Please run with -h to see help for further information. \nPress Enter to exit.' % args.rom)
        exit(1)
    if not os.path.isfile(args.rom):
        input('Could not find link sprite sheet at path %s. Please run with -h to see help for further information. \nPress Enter to exit.' % args.sprite)
        exit(1)

    # set up logger
    loglevel = {'error': logging.ERROR, 'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG}[args.loglevel]
    logging.basicConfig(format='%(message)s', level=loglevel)

    main(args)

