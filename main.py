
import sys
import string
import pygame as pg

ANTI_ALIAS_TEXT = True

def read_file_into_array(filename):
    out = []
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(8192)
            if chunk:
                out.extend(chunk)
            else:
                break
    return out

def as_printable(ch):
    if chr(ch) in string.printable:
        return chr(ch)
    else:
        return "."

class SourceFile:
    def __init__(self, from_file):
        self.filename    = from_file
        self.binary_data = read_file_into_array(from_file)

    def size(self):
        return len(self.binary_data)

    def __str__(self):
        return self.filename

class DiffLevel:
    def __init__(self, source_a, source_b, num_chunks):

        self.over_view  = []
        self.chunk_size = int(len(source_a) / num_chunks)
        chunk_offset = 0

        for i in range(num_chunks):
            diff_count = 0
            for x in range(self.chunk_size):
                b_a = source_a[chunk_offset + x]
                b_b = source_b[chunk_offset + x]
                if b_a != b_b: diff_count += 1

            similarity = ((self.chunk_size - diff_count) / self.chunk_size)

            if similarity < 0.25:
                self.over_view.append((255, 0, 0)) # red

            elif similarity < 0.5:
                self.over_view.append((255, 140, 0)) # orange

            elif similarity < 0.75:
                self.over_view.append((200, 255, 0)) # yellow

            else:
                self.over_view.append((0, 240, 0)) # green

            chunk_offset += self.chunk_size

    def max_sel(self):
        return len(self.over_view)-1

    def draw(self, screen, font, active, ypos, offset, count, selected):


        color = (100,100,100)
        if active:
            color = (255,255,255)
        xpos = 0

        surface=font.render(
                "chunk_size=$%x"%self.chunk_size,
                ANTI_ALIAS_TEXT,
                color)

        screen.blit(surface, (0, ypos))
        
        surface=font.render(
                "cur_offset=$%x+$%x"%(offset*self.chunk_size, self.chunk_size*selected),
                ANTI_ALIAS_TEXT,
                color)

        screen.blit(surface, (0, ypos+18))
        
        selected += offset

        #for diff_color in self.over_view:
        for x in range(count):
            pg.draw.rect(
                    screen,
                    self.over_view[offset],
                    (xpos, ypos + 37, 12, 16))

            if selected == offset:
                pg.draw.rect(
                        screen,
                        (0,0,0),
                        (xpos+1, ypos+38, 10, 14),
                        1)

                pg.draw.rect(
                        screen,
                        (255,255,255),
                        (xpos, ypos+37, 12, 16),
                        1)


            offset += 1
            xpos   += 12

class App:
    def __init__(self):
        pg.init();
        pg.font.init()
        self.screen = pg.display.set_mode([800, 600])
        pg.display.set_caption("graphical binary diff") 
        font_path = pg.font.match_font("Mono")
        print("using font: %s"%font_path)
        self.font = pg.font.Font(font_path, 15)

    def _inc_high_value(self):
        if self.high_sel < 63:
            self.high_sel += 1 
            self.repaint = True

    def _dec_high_value(self):
        if self.high_sel > 0: 
            self.high_sel -= 1
            self.repaint = True

    def _inc_mid_value(self):
        if self.mid_sel < 63: 
            self.mid_sel += 1 
            self.repaint = True

    def _dec_mid_value(self):
        if self.mid_sel > 0: 
            self.mid_sel -= 1
            self.repaint = True

    def _inc_low_value(self):
        if self.low_sel < 63: 
            self.low_sel += 1 
            self.repaint = True

    def _dec_low_value(self):
        if self.low_sel > 0: 
            self.low_sel -= 1
            self.repaint = True


    def main(self):

        args = sys.argv
        if len(args) != 3:
            print("please run `%s FILE1 FILE2`"%args[0])
            return -1

        file_a = SourceFile(args[1])
        print("file_a '%s'  size=%d"%(file_a, file_a.size()))

        file_b = SourceFile(args[2])
        print("file_b '%s'  size=%d"%(file_b, file_b.size()))

        if file_a.size() != file_b.size():
            print("file sizes do not match!")
            return -1

        cur_level = 0

        self.high_view = DiffLevel(file_a.binary_data, file_b.binary_data, 64)
        self.high_sel  = 0

        self.mid_view = DiffLevel(file_a.binary_data, file_b.binary_data, 4096)
        self.mid_sel  = 0

        self.low_view = DiffLevel(file_a.binary_data, file_b.binary_data, 262144)
        self.low_sel  = 0

        incrementors = (self._inc_high_value, self._inc_mid_value, self._inc_low_value)
        decrementors = (self._dec_high_value, self._dec_mid_value, self._dec_low_value)

        self.repaint = True

        while(True):
            pg.time.delay(20)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        if cur_level < 2: 
                            cur_level += 1
                            self.repaint = True

                    elif event.key == pg.K_ESCAPE:
                        if cur_level > 0: 
                            cur_level -= 1
                            self.repaint = True 

                    elif event.key == pg.K_LEFT: 
                        decrementors[cur_level]()


                    elif event.key == pg.K_RIGHT:
                        incrementors[cur_level]()

                        

            if self.repaint:
                self.repaint = False

                self.screen.fill((0,0,0))

                self.high_view.draw(
                        self.screen, 
                        self.font,
                        cur_level == 0,
                        0, 
                        0, 
                        64,
                        self.high_sel)

                if cur_level > 0:
                    self.mid_view.draw(
                            self.screen, 
                            self.font, 
                            cur_level == 1,
                            70, 
                            self.high_sel*64,
                            64,
                            self.mid_sel)


                if cur_level > 1:
                    offset = self.high_sel*64*64+self.mid_sel*64
                    self.low_view.draw(
                            self.screen,
                            self.font,
                            cur_level == 2,
                            140,
                            offset,
                            64,
                            self.low_sel)

                page_offset  = self.high_sel * self.high_view.chunk_size
                page_offset += self.mid_sel  * self.mid_view.chunk_size 
                page_offset += self.low_sel  * self.low_view.chunk_size
                page_offset -= 32


                ypos = 300
                for x in range(10):
                    if page_offset < 0 or page_offset >= len(file_a.binary_data):
                        text = "---------"
                    else:
                        # XXXX-XXXX  XX XX XX XX XX XX XX XX CCCCCCCC | CCCCCCCC XX XX XX XX XX XX XX XX

                        # page offset
                        text = text = "%04x-%04x  "%((page_offset>>16)&0xffff, page_offset&0xffff)

                        # file A HEX
                        text += "%02x %02x %02x %02x %02x %02x %02x %02x "%(
                                file_a.binary_data[page_offset],
                                file_a.binary_data[page_offset+1],
                                file_a.binary_data[page_offset+2],
                                file_a.binary_data[page_offset+3],
                                file_a.binary_data[page_offset+4],
                                file_a.binary_data[page_offset+5],
                                file_a.binary_data[page_offset+6],
                                file_a.binary_data[page_offset+7])
                        
                        # file A char
                        text += "%c%c%c%c%c%c%c%c | "%( 
                                as_printable(file_a.binary_data[page_offset]),
                                as_printable(file_a.binary_data[page_offset+1]),
                                as_printable(file_a.binary_data[page_offset+2]),
                                as_printable(file_a.binary_data[page_offset+3]),
                                as_printable(file_a.binary_data[page_offset+4]),
                                as_printable(file_a.binary_data[page_offset+5]),
                                as_printable(file_a.binary_data[page_offset+6]),
                                as_printable(file_a.binary_data[page_offset+7]))

                        # file B char
                        text += "%c%c%c%c%c%c%c%c "%( 
                                as_printable(file_b.binary_data[page_offset]),
                                as_printable(file_b.binary_data[page_offset+1]),
                                as_printable(file_b.binary_data[page_offset+2]),
                                as_printable(file_b.binary_data[page_offset+3]),
                                as_printable(file_b.binary_data[page_offset+4]),
                                as_printable(file_b.binary_data[page_offset+5]),
                                as_printable(file_b.binary_data[page_offset+6]),
                                as_printable(file_b.binary_data[page_offset+7]))

                        # file B hex
                        text += "%02x %02x %02x %02x %02x %02x %02x %02x"%(
                                file_b.binary_data[page_offset],
                                file_b.binary_data[page_offset+1],
                                file_b.binary_data[page_offset+2],
                                file_b.binary_data[page_offset+3],
                                file_b.binary_data[page_offset+4],
                                file_b.binary_data[page_offset+5],
                                file_b.binary_data[page_offset+6],
                                file_b.binary_data[page_offset+7])


                    color = (100,100,100)
                    if x==4 or x==5:
                        color = (255,255,255)
                    
                    surface=self.font.render(text, ANTI_ALIAS_TEXT, color) 
                    self.screen.blit(surface, (0, ypos))

                    ypos += 20
                    page_offset += 8

                pg.display.flip()

if __name__ == "__main__": App().main()



#class App:
#    def __init__(self):
#        pg.init();
#        pg.font.init()
#        self.screen = pg.display.set_mode([800, 600])
#        pg.display.set_caption("graphical binary diff") 
#
#    def main(self):
#
#        args = sys.argv
#        if len(args) != 3:
#            print("please run `%s FILE1 FILE2`"%args[0])
#            return -1
#
#        file_a = SourceFile(args[1])
#        print("file_a '%s'  size=%d"%(file_a, file_a.size()))
#
#        file_b = SourceFile(args[2])
#        print("file_b '%s'  size=%d"%(file_b, file_b.size()))
#
#        if file_a.size() != file_b.size():
#            print("file sizes do not match!")
#            return -1
#
#        over_view  = []
#        chunk_size = int(file_a.size() / 50)
#        chunk_offset = 0
#        for i in range(50):
#            diff_count = 0
#            for x in range(chunk_size):
#                b_a = file_a.binary_data[chunk_offset + x]
#                b_b = file_b.binary_data[chunk_offset + x]
#                if b_a != b_b: diff_count += 1
#
#            similarity = ((chunk_size - diff_count) / chunk_size)
#
#            if similarity < 0.25:
#                over_view.append((255, 0, 0)) # red
#
#            elif similarity < 0.5:
#                over_view.append((255, 140, 0)) # orange
#
#            elif similarity < 0.75:
#                over_view.append((200, 255, 0)) # yellow
#
#            else:
#                over_view.append((0, 240, 0)) # green
#
#            chunk_offset += chunk_size
#
#        while(True):
#            pg.time.delay(20)
#
#            for event in pg.event.get():
#                if event.type == pg.QUIT:
#                    return
#
#            xpos = 0
#            for diff_color in over_view:
#                pg.draw.rect(
#                        self.screen,
#                        diff_color,
#                        (xpos, 0, xpos+16, 16))
#                xpos += 16
#
#            pg.display.flip()
#
#if __name__ == "__main__": App().main()
