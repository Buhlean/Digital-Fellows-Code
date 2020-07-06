from youtube_transcript_api import YouTubeTranscriptApi
import getpass
import tkinter as tk
from tkinter import filedialog

BG_COLOUR = '#111111'
TEXT_COLOUR = '#ffffff'
LABELTEXT_COLOUR = '#ffffff'
BUTTON_COLOUR = '#b25c11'
CLICKED_COLOUR = '#444444'
ENTRYBG_COLOUR = '#222222'
BUTTONTEXT_COLOUR = '#ffffff'

class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Subtitle Extractor')
        self.configure(bg=BG_COLOUR)
        self.geometry('600x240+40+40')
        self.resizable(True, True)
        self.app = App(self)
        self.bind('<Return>',   self.app.extract)
        self.bind('<Escape>',   (lambda e: self.destroy()) ) # without this "hack", it would call destroy right here and cease to exist. 

class App(tk.Frame):
    def __init__(self, root):
        super().__init__(bg=BG_COLOUR, bd=0, relief=tk.GROOVE, padx=20, pady=20)
        self.outpath        = tk.StringVar(self, f'C:/Users/{getpass.getuser()}/Downloads')
        self.error          = tk.StringVar(self, '')
        self.url_field      = tk.StringVar(self, '')
        self.path, self.filename = '', ''
        
        self.pack(side="top", fill="both", expand=True)
        
        # last line:
        self.drawGUI()

    def drawGUI(self):
        self.padding = 6
        self.columns = 6
        self.drawurl_field()
        self.drawoutput()
        self.drawother()
        
    def drawurl_field(self):
        frameurl_field = tk.Frame(self)
        frameurl_field.configure(pady=self.padding, bg=BG_COLOUR)
        frameurl_field.columnconfigure(1, weight=1)
        frameurl_field.pack(side=tk.TOP, fill=tk.X)
        #Label URL
        tk.Label(frameurl_field, anchor='nw', bg=BG_COLOUR, font=("Helvetica", "13"), bd=0, fg=LABELTEXT_COLOUR, justify=tk.LEFT,
                 text='Please provide the YouTube URL or the video ID:'
                 ).grid(columnspan=3, sticky='NEWS', pady=(0,8))
        #Entry URL
        tk.Entry(frameurl_field, bg=ENTRYBG_COLOUR, font=("Helvetica", "13"), bd=0, fg=TEXT_COLOUR, justify=tk.LEFT,
                 width=40, highlightthickness=0, textvariable=self.url_field,
                 ).grid(columnspan=2, row=1, sticky='NEWS', ipady=4, padx=(0,8))
        tk.Label(frameurl_field, bg=BG_COLOUR, bd=0, width=12).grid(column=2, row=1, sticky='NEWS') # emulates button
        
    def drawoutput(self):
        frameoutput = tk.Frame(self)
        frameoutput.configure(pady=self.padding, bg=BG_COLOUR)
        frameoutput.columnconfigure(1, weight=1)
        frameoutput.pack(side=tk.TOP, fill=tk.X)
        #LabelOutput
        tk.Label(frameoutput, anchor='nw', bg=BG_COLOUR, font=("Helvetica", "13"), bd=0, fg=LABELTEXT_COLOUR,
                 justify=tk.LEFT, text='Where should the output go? (optional)'
                 ).grid(columnspan=5, sticky='NEWS', pady=(0,8))
        #EntryOutput
        tk.Entry(frameoutput, bg=ENTRYBG_COLOUR, font=("Helvetica", "13"),
                 bd=0, fg=TEXT_COLOUR, justify=tk.LEFT, 
                 highlightthickness=0,
                 textvariable=self.outpath
                 ).grid(column=1, row=1, sticky='NEWS', padx=(0,8))
        #ButtonOutput
        tk.Button(frameoutput, activebackground='#aaaaaa', activeforeground=CLICKED_COLOUR, bd=1, bg=BUTTON_COLOUR, command=self.getsaveplace,
                  fg=BUTTONTEXT_COLOUR, font=("Helvetica", "13"), padx=0, pady=0, highlightcolor=CLICKED_COLOUR, relief=tk.RAISED, text='Choose...', width=9
                  ).grid(column=3, row=1, sticky='EW')
    def drawother(self):
        tk.Button(self, activebackground='#7a7e8f', activeforeground=CLICKED_COLOUR, bd=1, bg=BUTTON_COLOUR,
                  command=self.extract, fg=BUTTONTEXT_COLOUR, font=("Helvetica", "13"), padx=0, pady=0,
                  highlightcolor=CLICKED_COLOUR, relief=tk.RAISED, text='Extract', width=9
                  ).pack(side=tk.RIGHT) #ButtonSubmit
        tk.Label(self, bg=BG_COLOUR, font=("Helvetica", "13"),
                 bd=0, fg=LABELTEXT_COLOUR, textvariable=self.error).pack(side=tk.RIGHT, padx=(0,8))

        
    def getsaveplace(self, e=None):
        self.error.set('')
        self.outpath.set(filedialog.askdirectory())
    def extract(self, e=None):
        self.error.set('')
        url_or_id = self.url_field.get()
        if 10 < len(url_or_id) < 14:
            video_id    = url_or_id
        elif 'youtu.be' in url_or_id:
            tail        = url_or_id.split('.be/')[1]
            video_id    = tail.split('?')[0]
        elif 'youtube' in url_or_id:
            tail        = url_or_id.split('/watch?')[1]
            tail        = tail.split('&')[0]
            video_id    = tail.split('v=')[1]
        else:
            self.error.set('The URL/ID is not in the standard format, please correct that.')
            return

        if '/' in self.outpath.get():
            self.path = self.outpath.get()
            self.filename = video_id
        else:
            self.error.set('Please specify a valid input path and file')
            return

        final_text = ''
        try:
            list_of_cues_in_dicts = YouTubeTranscriptApi.get_transcript(video_id, languages=('de',))
        except Exception as e:
            self.error.set('Error occurred while fetching from YouTube, check URL')
            return
        
        for cue in list_of_cues_in_dicts:
            final_text = ' '.join((final_text, cue['text']))
        final_text = final_text[1:]

        with open(''.join((self.path, '/', self.filename, '.vtt')), 'w') as file:
            file.write(final_text)
        self.error.set('Success!')

def main():
    root = Root()
    root.mainloop()

if __name__ == '__main__':
    main()
