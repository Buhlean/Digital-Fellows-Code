from youtube_transcript_api import YouTubeTranscriptApi
import getpass
import json
#import pyttsx3
#import re
import spellchecker
import tkinter as tk
from tkinter import filedialog

DEBUG = True

class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TEXT['TITLE'])
        self.configure(bg = COLOUR['FRAME_BG'])
        self.geometry('1000x600+20+20')
        self.resizable(True, True)

        self.app = App(self)

        self.bind_all('<Control-s>', self.app.save_text)

        if DEBUG: print('FINISHED, STARTING MAIN LOOP')

class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg = COLOUR['FRAME_BG_CONTRAST'], bd = 0)
        self.pack(fill=tk.BOTH, expand=True)

        self.padding            = 6 #px
        self.colour             = tk.StringVar(self, 'DARK')
        self.language           = tk.StringVar(self, 'EN')
        self.state              = tk.IntVar(self, 0)
        self.data               = {}
        self.received           = False

        self.elements = {}
        self.content = {}

        if DEBUG: print('APP INITIALIZED')

        self.draw_GUI()

    def draw_GUI(self, e=None, *, redraw=False):
        if not redraw:
            self.elements['CONTENT']= tk.Frame(self, bg = COLOUR['FRAME_BG'], bd = 0, padx=8, pady=8)
            self.elements['CONTENT'].pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.elements['CONTENT'].rowconfigure(0, minsize=10)
            self.elements['CONTENT'].rowconfigure(1, minsize=300, weight=1)
            for i in range(24): self.elements['CONTENT'].columnconfigure(i, minsize=32)
            self.elements['CONTENT'].columnconfigure(20, weight=1, minsize=20)

            self.elements['FETCH']  = tk.Frame(self.elements['CONTENT'], bg = COLOUR['FRAME_BG'], bd = 0, padx=8, )
            self.elements['TEXT']   = tk.Frame(self.elements['CONTENT'], bg = COLOUR['FRAME_BG'], bd = 0, padx=8, )
            self.elements['TOOL']   = tk.Frame(self.elements['CONTENT'], bg = COLOUR['FRAME_BG'], bd = 0, padx=8, )

            self.content['FETCH']   = Subtitle_Widget(self.elements['FETCH'])
            self.content['TEXT']    = Text_Widget(self.elements['TEXT'])
            self.content['TOOL']    = Tools_Widget(self.elements['TOOL'])

            if DEBUG: print('ALL: drawn')
        else:
            if DEBUG: print('ALL: redrawn')
        #colour
        self.configure(bg=COLOUR['FRAME_BG_CONTRAST'],)
        self.master.configure(bg = COLOUR['FRAME_BG_CONTRAST'],)
        self.elements['CONTENT'].configure(bg = COLOUR['FRAME_BG_CONTRAST'],)
        self.elements['FETCH'].configure(bg = COLOUR['FRAME_BG'],)
        self.elements['TEXT'].configure(bg = COLOUR['FRAME_BG'],)
        self.elements['TOOL'].configure(bg = COLOUR['FRAME_BG'],)

        self.draw_tabs(redraw=redraw)
        self.draw_content(redraw=redraw)
        
    def draw_tabs(self, e=None, *, redraw=False):
        target_colour = 'LIGHT' if 'DARK' in self.colour.get() else 'DARK'
        target_language = 'DE' if 'EN' in self.language.get() else 'EN'
        if not redraw:
            self.elements['TAB_DL'] = tk.Button(self.elements['CONTENT'])
            self.elements['TAB_DL'].configure(relief=tk.FLAT, command=(lambda:self.tab_clicked(which=0)))
            self.elements['TAB_DL'].grid(row=0, column=0, columnspan=5, sticky='NEWS', padx=(8,0))
            
            self.elements['TAB_TOOLS'] = tk.Button(self.elements['CONTENT'])
            self.elements['TAB_TOOLS'].configure(relief=tk.FLAT, command=(lambda:self.tab_clicked(which=1)))
            self.elements['TAB_TOOLS'].grid(row=0, column=6, columnspan=5, sticky='NEWS', padx=(8,0))

            self.elements['LANGUAGE_BLOB'] = tk.Radiobutton(self.elements['CONTENT'])
            self.elements['LANGUAGE_BLOB'].configure( indicatoron = False, width = 2, borderwidth = 1,
                command = self.change_language, highlightthickness = 0, padx = 0, pady = 0,
                offrelief = tk.FLAT, relief = tk.FLAT, variable = self.language, )
            self.elements['LANGUAGE_BLOB'].grid(row = 0, column = 22, sticky='NES', pady=(0, 8))
            
            self.elements['COLOUR_BLOB'] = tk.Radiobutton(self.elements['CONTENT'])
            self.elements['COLOUR_BLOB'].configure( indicatoron = False, width = 2, borderwidth = 1,
                command = self.change_colour_scheme, highlightthickness = 0, padx = 0, pady = 0,
                offrelief = tk.FLAT, relief = tk.FLAT, variable = self.colour,)
            self.elements['COLOUR_BLOB'].grid(row = 0, column = 23, sticky='NES', pady=(0, 8))

            if DEBUG: print('TABS: drawn')
        else:
            if DEBUG: print('TABS: redrawn')
        #colour
        self.elements['COLOUR_BLOB'].configure(activebackground = COLOURS[target_colour]['FRAME_BG'], value = target_colour,
                background = COLOURS[target_colour]['FRAME_BG'], highlightbackground = COLOURS[target_colour]['FRAME_BG'],
                highlightcolor = COLOURS[target_colour]['FRAME_BG'], selectcolor = COLOURS[target_colour]['FRAME_BG'],)
        self.elements['LANGUAGE_BLOB'].configure(activebackground = COLOUR['FRAME_BG'], value = target_language,
                background = COLOUR['FRAME_BG'], highlightbackground = COLOUR['FRAME_BG'], fg=COLOUR['TEXT'], text=target_language,
                highlightcolor = COLOUR['FRAME_BG'], selectcolor = COLOUR['FRAME_BG'], activeforeground=COLOUR['TEXT'])
        self.elements['TAB_DL'].configure(bg = COLOUR['FRAME_BG'], activebackground = COLOUR['FRAME_BG'],)
        self.elements['TAB_TOOLS'].configure(bg = COLOUR['FRAME_BG'], activebackground = COLOUR['FRAME_BG'],)

    def draw_content(self, e=None, *, redraw=False):
        if self.state.get() == 0:
            self.elements['TOOL'].lower()
            self.elements['FETCH'].lift()
            
            self.elements['FETCH'].grid(row = 1, column = 0, columnspan = 12, sticky = 'NEWS', padx = (0,2))
            self.content['FETCH'].draw_GUI(redraw = redraw)
            
            self.elements['TEXT'].grid(row = 1, column = 12, columnspan = 12, sticky = 'NEWS', padx = (0,0))
            self.content['TEXT'].draw_GUI(redraw = redraw)

            self.elements['TAB_DL'].configure(bg = COLOUR['FRAME_BG'], activebackground = COLOUR['FRAME_BG'],)
            self.elements['TAB_TOOLS'].configure(bg = COLOUR['TAB_OFF'], activebackground = COLOUR['FRAME_BG'],)
        
            if DEBUG: print('TAB 0: drawn')
        else:
            self.elements['FETCH'].lower()
            self.elements['TOOL'].lift()

            self.elements['TOOL'].grid(row = 1, column = 0, columnspan = 8, sticky = 'NEWS', padx = (0,2))
            self.content['TOOL'].draw_GUI(redraw = redraw)

            self.elements['TEXT'].grid(row = 1, column = 8, columnspan = 16, sticky = 'NEWS', padx = (0,0))
            self.content['TEXT'].draw_GUI(redraw = redraw)

            self.elements['TAB_DL'].configure(bg = COLOUR['TAB_OFF'], activebackground = COLOUR['FRAME_BG'],)
            self.elements['TAB_TOOLS'].configure(bg = COLOUR['FRAME_BG'], activebackground = COLOUR['FRAME_BG'],)

            if DEBUG: print('TAB 1: drawn')
            
    def tab_clicked(self, e=None, *, which=0):
        if which == 0 and self.state.get() != 0:
                self.state.set(0)
                self.kill_all()
                self.draw_content()
        if which == 1 and self.state.get() != 1:
                self.state.set(1)
                self.kill_all()
                self.draw_content()

    def kill_all(self, e=None):
        for element in [self.content['FETCH'], self.content['TEXT'], self.content['TOOL']]:
            element.kill()
                
    def change_colour_scheme(self, e=None):
        COLOUR.update(COLOURS[self.colour.get()])
        if DEBUG: print('COLOUR: changed to:', self.colour.get())
        self.draw_GUI(redraw=True)

    def change_language(self, e=None, ):
        TEXT.update(TEXTS[self.language.get()])
        ERR.update(ERRS[self.language.get()])
        if DEBUG: print('LANGUAGE: changed to:', self.language.get())
        self.draw_GUI(redraw=True)

    def receive_transcript_data(self, cues, video_id, path, code):
        if self.received: return False
        self.received = True
        self.data.update({'CUES': cues, 'VIDEO_ID': video_id, 'PATH': path, 'CODE': code})

    def display_transcript_using_received_transcript_data(self):
        if not self.received: return False
        self.content['TEXT'].receive_and_display_transcript(data = self.data)

    def save_text(self, e=None):
        self.content['TEXT'].save_text(e=e)

######## TOOLS ##########################################################################################
        
class Tools_Widget(tk.Frame):

    '''
    All the Buttons and functionality for the editor
    Usually displayed on the right when not currently donwloading subtitles
    '''
    
    def __init__(self, root):
        super().__init__(root, bg = COLOUR['FRAME_BG'], bd = 0, )
        self.pack(side="top", fill=tk.BOTH, expand=True,)

        self.fetched_and_ready = False
        self.speech_defunct = False # preliminarily
        
        self.elements = {}
        
        self.possible_languages = [('en', 'en - English'), ('es', 'es - Espanol'), ('de', 'de - Deutsch'), ('fr', 'fr - Francois'), ('pt', 'pt - Portugues')]
        self.clicked_language = tk.StringVar(self, TEXT['TOOL_DEFAULT_DICT'])
        self.spellchecker = None
        self.spellcheck_iter = []

        self.text = self.master.master.master.content['TEXT'] 
        
    def draw_GUI(self, e=None, *, redraw=False):
        if not redraw:
            self.elements['BG'] = tk.Frame(self)
            self.elements['BG'].pack(fill = tk.BOTH, expand=True, padx=0, pady=0 )
            self.elements['BG'].columnconfigure(0, weight=1)
            self.elements['BG'].rowconfigure(12, weight=1)

            self.elements['SAVE_LABEL']=tk.Label(self.elements['BG'])
            self.elements['SAVE_LABEL'].configure(anchor='nw', font=FONT, bd=0, justify=tk.LEFT, )
            self.elements['SAVE_LABEL'].grid(column=0, row=0, sticky='NEWS', pady=(8,0))
            
            self.elements['SAVE_BUTTON']=tk.Button(self.elements['BG'])
            self.elements['SAVE_BUTTON'].configure( bd=1, justify=tk.LEFT, command=self.save_text_in_file, font=FONT, relief=tk.RAISED, pady=0, )
            self.elements['SAVE_BUTTON'].grid(column=0, row=1, sticky='NEWS', pady=4)

            self.elements['SPELLCHECK']=tk.Label(self.elements['BG'])
            self.elements['SPELLCHECK'].configure(anchor='nw', font=FONT, bd=0, justify=tk.LEFT, )
            self.elements['SPELLCHECK'].grid(column=0, row=2, sticky='NEWS', pady=(8,0))

            self.elements['DICT_LANG']=tk.Menubutton(self.elements['BG'])
            self.elements['DICT_LANG'].configure(bd=1, justify=tk.LEFT, anchor='w', font=FONT, padx=6, pady=0, relief=tk.RAISED, textvariable=self.clicked_language)
            self.elements['DICT_LANG'].grid(column=0, row=3, sticky='EW', padx=(0,8), ipady=4, pady=4) 
            self.elements['DICT_LANG'].menu=tk.Menu(self.elements['DICT_LANG'])
            self.elements['DICT_LANG'].menu.configure(tearoff=0, bd=0, font=FONT)
            self.elements['DICT_LANG']['menu']=self.elements['DICT_LANG'].menu
            for code, text in self.possible_languages:
                self.elements['DICT_LANG'].menu.add_radiobutton(value=code, label=text, variable=self.clicked_language, )#command=self.change_dict_lang)

            self.elements['CHECK_BUTTON']=tk.Button(self.elements['BG'])
            self.elements['CHECK_BUTTON'].configure( bd=1, justify=tk.LEFT, command=self.spellcheck_all, font=FONT, relief=tk.RAISED, pady=0, )
            self.elements['CHECK_BUTTON'].grid(column=0, row=4, sticky='NEWS', pady=4)

            self.elements['SPEECH_LABEL']=tk.Label(self.elements['BG'])
            self.elements['SPEECH_LABEL'].configure(anchor='nw', font=FONT, bd=0, justify=tk.LEFT, )
            self.elements['SPEECH_LABEL'].grid(column=0, row=5, sticky='NEWS', pady=(8,0))
            
            self.elements['SPEECH_BUTTON']=tk.Button(self.elements['BG'])
            self.elements['SPEECH_BUTTON'].configure( bd=1, justify=tk.LEFT, command=self.speak, font=FONT, relief=tk.RAISED, pady=0, )
            self.elements['SPEECH_BUTTON'].grid(column=0, row=6, sticky='NEWS', pady=4)

            # cut copy paste buttons?
            
            if DEBUG: print('TOOL BG: drawn')
        else:
            if DEBUG: print('TOOL BG: redrawn')
        #colour
        self.configure(bg = COLOUR['FRAME_BG'],)
        self.elements['BG'].configure(bg = COLOUR['FRAME_BG'],)
        self.elements['SAVE_LABEL'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['TOOL_SAVE'])
        self.elements['SAVE_BUTTON'].configure(fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['TOOL_SAVE_B'],
            activeforeground = COLOUR['ACTIVE'], activebackground = COLOUR['BUTTON_CLICKED'], highlightcolor = COLOUR['ACTIVE'],)
        self.elements['SPELLCHECK'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['TOOL_SPELL'])
        self.elements['DICT_LANG'].configure(fg = COLOUR['TEXT'], activeforeground = COLOUR['TEXT'],
            bg = COLOUR['SELECT_BG'], activebackground = COLOUR['SELECT_BG_ACTIVE'], text = TEXT['TOOL_DEFAULT_DICT'],)
        self.elements['DICT_LANG'].menu.configure(activeforeground = COLOUR['CHOICE_FG_ACTIVE'],fg = COLOUR['CHOICE_FG'],
            activebackground = COLOUR['CHOICE_BG_ACTIVE'], bg = COLOUR['CHOICE_BG'],)
        self.elements['CHECK_BUTTON'].configure(fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['TOOL_SPELL_B'],
            activeforeground = COLOUR['ACTIVE'], activebackground = COLOUR['BUTTON_CLICKED'], highlightcolor = COLOUR['ACTIVE'],)
        self.elements['SPEECH_LABEL'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['TOOL_SPEECH'] if not self.speech_defunct else TEXT['SPEECH_UNAVAILABLE'])
        self.elements['SPEECH_BUTTON'].configure(fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['TOOL_SPEECH_B'],
            activeforeground = COLOUR['ACTIVE'], activebackground = COLOUR['BUTTON_CLICKED'], highlightcolor = COLOUR['ACTIVE'],)
        
    def speak(self):
        if not self.text.speak():
            self.speech_defunct = True
            self.elements['SPEECH_LABEL'].configure(text=TEXT['SPEECH_UNAVAILABLE'])
            self.elements['SPEECH_BUTTON'].configure(state=tk.DISABLED)
    
    def save_text_in_file(self):
        self.text.save_text()
        return

    def spellcheck_create(self, lang=None):
        if lang is None:
            language = self.clicked_language.get()
            if DEBUG: print('LANGUAGE CHOSEN BY USER')
        else:
            language = lang
            if DEBUG: print('LANGUAGE FOUND IN FILENAME')
        if len(language) != 2:
            if DEBUG: print('ABORT SPELLCHECK')
            return False
        self.spellchecker = spellchecker.SpellChecker(language)
        if DEBUG: print('SPELLCHECKER: created: ', self.spellchecker)
        return

    def spellcheck_all(self, lang=None):
        if not self.text.loaded: return
        if not self.spellcheck_create(lang=lang): return
        self.text.delete_all_mistakes_tags()

        to_check = set()
        words = self.text.elements['TEXT'].get('1.0', "end-1c").split()
        if DEBUG: print('TEXT SPLIT FOR PROCESSING')

        import re
        regex = re.compile("[^a-zA-Z]")
        if DEBUG: print('REGEX SUCCESS')
        
        for word in words:
            if 'http://' in word or 'www.' in word: continue
            # ALT: s = ''.join(filter(str.isalnum, s))
            to_check.add(regex.sub('', word))
        if DEBUG: print('Words to spellcheck: ', len(to_check))
        
        self.spellcheck_iter = iter(self.spellchecker.unknown(to_check))
        self.master.master.after(0, self.advance_spellchecking) # schedule
        if DEBUG: print('SPELLCHECKING SCHEDULED')
        
    def spellcheck_part(self, a, b):
        if self.spellchecker is None: self.spellcheck_create()
        if not self.text.loaded: return
        self.spellcheck_iter = iter(self.spellchecker.unknown(self.text.elements['TEXT'].get(a, b).split()))
        self.master.master.after(0, self.advance_spellchecking) # schedule
        if DEBUG: print('SPELLCHECKING SCHEDULED')

    def advance_spellchecking(self):
        try:
            word = next(self.spellcheck_iter)
        except StopIteration:
            if DEBUG: print('SPELLCHECKING: stopped.')
            return
        if len(word) > 3:
            self.text.search_and_flag(word)
        self.master.master.after(0, self.advance_spellchecking) # schedule
    
    def kill(self, e=None):
        for widget in self.winfo_children():
            widget.destroy()

######## TEXT EDITOR ####################################################################################
            
class Text_Widget(tk.Frame):
    '''
    Contains the Text widget
    Remembers the content and spellcheck information
    Can receive data from the Download widget
    '''
    def __init__(self, root):
        super().__init__(root, bg = COLOUR['FRAME_BG'], bd = 0)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(4,0))

        self.loaded = False
        self.received = False
        self.text = ''
        self.elements = {}
        self.marked = False
        self.tools = None

    def draw_GUI(self, e=None, *, redraw=False):
        if not redraw:
            self.tools = self.master.master.master.content['TOOL']
            
            self.elements['BG'] = tk.Frame(self)
            self.elements['BG'].pack(side = tk.TOP, fill = tk.BOTH, expand=True, padx=0 )
            for i in range(3): self.elements['BG'].columnconfigure(i, weight=1)
            self.elements['BG'].rowconfigure(2, weight=1)
            if DEBUG: print('TEXT BG: drawn')
        else:
            if DEBUG: print('TEXT BG: redrawn')
        #colour
        self.configure(bg = COLOUR['FRAME_BG'],)
        self.elements['BG'].configure(bg = COLOUR['FRAME_BG'],)
        if self.loaded:
            if not redraw:
                self.elements['TEXT'] = tk.Text(self.elements['BG'])
                self.elements['TEXT'].grid(row=2, column=0, columnspan=3, padx=0, sticky='NEWS')
                self.elements['TEXT'].configure(insertbackground=COLOUR['TEXT'], padx=6, pady=6, bd=2,
                                                font=FONT, relief=tk.FLAT, spacing3=.1, wrap=tk.WORD )
                if DEBUG: print('TEXT: drawn')
            else:
                if DEBUG: print('TEXT: redrawn')
            #colour
            self.elements['TEXT'].configure(bg = COLOUR['ENTRY_BG'], fg = COLOUR['TEXT'],)
            self.display_text()
        else:
            if not redraw:
                self.elements['EXPLAIN_LOAD'] = tk.Label(self.elements['BG'])
                self.elements['EXPLAIN_LOAD'].configure(anchor = 'nw', font = FONT, bd = 0, justify = tk.LEFT, width=40, )
                self.elements['EXPLAIN_LOAD'].grid(columnspan = 3, sticky = 'NEWS', pady = 6, padx=0)
                self.elements['LOAD_BUTTON'] = tk.Button(self.elements['BG'])
                self.elements['LOAD_BUTTON'].configure( bd = 1, command = self.load_text_file, font = FONT,
                    pady = 0, relief = tk.RAISED, width = 16, justify = tk.LEFT, )
                self.elements['LOAD_BUTTON'].grid(column = 0, row = 1, sticky = 'W', padx = 0, pady=2)
                if DEBUG: print('TEXT BUTTON: drawn')
            else:
                if DEBUG: print('TEXT BUTTON: redrawn')
            #colour
            self.elements['EXPLAIN_LOAD'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['EXPLAIN'])
            self.elements['LOAD_BUTTON'].configure(fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['B_LOAD_FILE'],
                activeforeground = COLOUR['ACTIVE'], activebackground = COLOUR['BUTTON_CLICKED'], highlightcolor = COLOUR['ACTIVE'],)
                
    def load_text_file(self, e=None, ):
        if DEBUG: print('FILE: attempt to load')
        file = (filedialog.askopenfilename())
        if file is None or file == '': return
        with open(file, 'r') as transcript:
            self.text = list(transcript)
        if DEBUG: print('FILE: loaded')
        self.loaded = True
        self.received = False
        self.kill()
        self.draw_GUI()
        self.display_text()
        # trying to guess the language from the filename:
        parts = file.split('_')
        code = ''
        for maybe_code in parts:
            if len(maybe_code) == 2:
                if maybe_code in ['en', 'es', 'de', 'fr' 'pt']:
                    code = maybe_code
                    self.spellchecker = spellchecker.SpellChecker(language=code)
        if code is not None and code != '':
            self.language = code
            self.tools.spellcheck_all(lang = self.language)
        self.master.master.master.after(0, self.master.master.master.elements['TAB_TOOLS'].invoke)
                                        
    def receive_and_display_transcript(self, data):
        self.text = data['CUES']
        self.loaded = True
        self.kill()
        self.draw_GUI()

    def display_text(self):
        self.elements['TEXT'].delete('1.0', 'end')
        self.elements['TEXT'].insert('1.0', '\n'.join(self.text))
        if DEBUG: print('TEXT: displayed')

    def save_text(self, e=None):
        if not self.loaded: return
        file = filedialog.asksaveasfilename()
        if file is None: return
        with open(file, 'w') as save_place:
            for line in self.elements['TEXT'].get('1.0', 'end'):
                save_place.write(line)

    def speak(self):
        if not self.loaded: return True
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(self.elements['TEXT'].selection_get())
            engine.runAndWait()
            return True
        except:
            return False
        return False
    
    def search_and_flag(self, word):
        if not self.loaded: return False
        characters = str(len(word))
        startInd = '1.0'
        while(startInd):
            startInd = self.elements['TEXT'].search(word, startInd, stopindex='end')
            if startInd:
                startInd = str(startInd)
                lastInd = ''.join((startInd, '+', characters, 'c'))
                self.elements['TEXT'].tag_add('misspell', startInd, lastInd)
                startInd = lastInd
        if not self.marked:
            self.elements['TEXT'].tag_config('misspell', background="red", foreground="white")
            self.marked = True

    def delete_all_mistakes_tags(self):
        if not self.loaded: return False
        self.elements['TEXT'].tag_delete('misspell')
        self.marked = False
        
    def kill(self, e=None):
        for widget in self.winfo_children():
            widget.destroy()

######## SUBTITLE DOWNLOAD ##############################################################################
            
class Subtitle_Widget(tk.Frame):
    '''
    Download Subtitles from here
    Provide a URL, an OUTPUT_PATH, some FORMAT, and a LANGUAGE,
    then let YouTube_transcript_API do the work
    Sends the transcript to the Text widget once done.
    '''
    def __init__(self, root):
        super().__init__(root, bg = COLOUR['FRAME_BG_CONTRAST'], bd = 0, )
        self.pack(side="top", fill=tk.BOTH, expand=True, pady=(4,0))
        
        self.elements           = {}
        self.outpath            = tk.StringVar(self, f'C:/Users/{getpass.getuser()}/Downloads')
        self.outpath.trace_add("write", lambda a, b, c: self.path_changed())
        self.error              = tk.StringVar(self, '') # displays all status messages prominently
        self.url_field          = tk.StringVar(self, '') if not DEBUG else tk.StringVar(self, 'youtube.com/watch?v=6Af6b_wyiwI')
        self.url_field.trace_add("write", lambda a, b, c: self.id_changed())
        self.selection          = tk.StringVar(self, 'Default: de, en') # currently selected languages
        
        self.format_text        = tk.IntVar(self, 1) # what files do you want to generate
        self.format_stamps      = tk.IntVar(self, 0) # "
        self.format_json        = tk.IntVar(self, 0) # "
        self.options_known      = False # user can just press a button as a hail mary
        self.possible_languages = []    # [(code, language, merged)]
        self.possible_translations = [] # "
        self.clicked_languages  = {}    # dict with lang-code as key
        self.clicked_translations = {}  # "
        self.transcript_list    = None  # generated by the youtube api library, contains <transcript metadata objects>

        self.padding            = 6 #px
        self.columns            = 6

    def draw_GUI(self, e=None, *, redraw = False): # "e=None" means that I might want to call this function via an Event which then wants to give its info to the function as a parameter. that's only possible if the function is ready for that. I made all functions ready for that because a whole lot changed during developement and I called almost every function via event at one point or another. you can ignore those for the most part.
        if redraw:
            self.configure(bg = COLOUR['FRAME_BG_CONTRAST'],)
        self.draw_url_field(redraw = redraw)
        self.draw_output(redraw = redraw)
        self.draw_format(redraw = redraw)
        self.draw_language(redraw = redraw)
        self.draw_other(redraw = redraw)
       
    def draw_url_field(self, e=None, *, redraw = False):
        if not redraw:
            self.elements['URL'] = tk.Frame(self)
            self.elements['URL'].configure(pady = self.padding)
            self.elements['URL'].columnconfigure(1, weight = 1)
            self.elements['URL'].pack(side = tk.TOP, fill = tk.X, pady = (0,0), padx = 0)
            self.elements['URL_LABEL'] = tk.Label(self.elements['URL'])
            self.elements['URL_LABEL'].configure(anchor = 'nw', font = FONT, bd = 0, justify = tk.LEFT, width=40, )
            self.elements['URL_LABEL'].grid(columnspan = 3, sticky = 'NEWS', pady = (0,8))
            self.elements['URL_FIELD'] = tk.Entry(self.elements['URL'])
            self.elements['URL_FIELD'].configure( font = FONT, bd = 0,  justify = tk.LEFT, width = 40, highlightthickness = 0, textvariable = self.url_field,)    
            self.elements['URL_FIELD'].grid(columnspan = 2, row = 1, sticky = 'NEWS', ipady = 4, padx = (0,8))
            self.elements['URL_FIELD'].focus_set()
            self.elements['URL_PAD1'] = tk.Label(self.elements['URL'])
            self.elements['URL_PAD1'].configure(bd = 0, width = 12,)
            self.elements['URL_PAD1'].grid(column = 2, row = 1, sticky = 'NEWS') # emulates button
            if DEBUG: print('SUBTITLES URL: drawn')
        else:
            if DEBUG: print('SUBTITLES URL: redrawn')
        # whether or not redraw:
        self.elements['URL'].configure(bg = COLOUR['FRAME_BG'])
        self.elements['URL_FIELD'].configure(bg = COLOUR['ENTRY_BG'], fg = COLOUR['TEXT'],)
        self.elements['URL_PAD1'].configure(bg = COLOUR['FRAME_BG'])
        self.elements['URL_LABEL'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['URL_INPUT'],)
        
    def draw_output(self, e=None, *, redraw = False):
        if not redraw:
            self.elements['OUTPUT'] = tk.Frame(self)
            self.elements['OUTPUT'].configure(pady = self.padding, bg = COLOUR['FRAME_BG'],)
            self.elements['OUTPUT'].columnconfigure(1, weight = 1)
            self.elements['OUTPUT'].pack(side = tk.TOP, fill = tk.X, pady = (0,0), padx = 0)
            self.elements['OUTPUT_LABEL'] = tk.Label(self.elements['OUTPUT'])
            self.elements['OUTPUT_LABEL'].configure(anchor = 'nw', font = FONT, bd = 0, justify = tk.LEFT,)
            self.elements['OUTPUT_LABEL'].grid(columnspan = 5, sticky = 'NEWS', pady = (0,8))
            self.elements['OUTPUT_FIELD'] = tk.Entry(self.elements['OUTPUT'])
            self.elements['OUTPUT_FIELD'].configure(font = FONT, bd = 0,  justify = tk.LEFT, highlightthickness = 0, textvariable=self.outpath,)
            self.elements['OUTPUT_FIELD'].grid(column = 1, row = 1, sticky = 'NEWS', padx = (0,8))
            self.elements['OUTPUT_BUTTON'] = tk.Button(self.elements['OUTPUT'])
            self.elements['OUTPUT_BUTTON'].configure( bd = 1, command = self.getsaveplace, font = FONT,
                padx = 0, pady = 0, relief = tk.RAISED, width = 9)
            self.elements['OUTPUT_BUTTON'].grid(column = 3, row = 1, sticky = 'EW')
            if DEBUG: print('SUBTITLES OUTPUT: drawn')
        else:
            if DEBUG: print('SUBTITLES OUTPUT: redrawn')
        self.elements['OUTPUT'].configure(bg = COLOUR['FRAME_BG'],)
        self.elements['OUTPUT_FIELD'].configure(bg = COLOUR['ENTRY_BG'], fg = COLOUR['TEXT'],)
        self.elements['OUTPUT_BUTTON'].configure(fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['CHOOSE'],
            activeforeground = COLOUR['ACTIVE'], activebackground = COLOUR['BUTTON_CLICKED'], highlightcolor = COLOUR['ACTIVE'],)
        self.elements['OUTPUT_LABEL'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['OUTPUT'],)

    def draw_format(self, e=None, *, redraw = False):
        if not redraw:
            self.elements['FORMAT'] = tk.Frame(self)
            self.elements['FORMAT'].configure(pady = self.padding,)
            for i in range(self.columns+2):
                self.elements['FORMAT'].columnconfigure(i, weight = 4)
            self.elements['FORMAT'].pack(side = tk.TOP, fill = tk.X, pady = (0,1), padx = 0)
            self.elements['FORMAT_LABEL'] = tk.Label(self.elements['FORMAT'])
            self.elements['FORMAT_LABEL'].configure(anchor = 'nw', font = FONT, bd = 0, justify = tk.LEFT, )
            self.elements['FORMAT_LABEL'].grid(columnspan = self.columns, sticky = 'NEWS', pady = (0,8))
            self.elements['FORMAT_BOX_TEXT'] = tk.Checkbutton(self.elements['FORMAT'])
            self.elements['FORMAT_BOX_TEXT'].configure(variable = self.format_text, command=self.format_changed, 
                width = 3, anchor = 'nw', font = FONT, bd = 0, pady = 0, padx = 4, justify = tk.LEFT,)
            self.elements['FORMAT_BOX_TEXT'].grid(column = 0, row = 1, sticky = 'NEWS')
            self.elements['FORMAT_BOX_CUES'] = tk.Checkbutton(self.elements['FORMAT'])
            self.elements['FORMAT_BOX_CUES'].configure(variable = self.format_json, command=self.format_changed, 
                width = 3, anchor = 'nw', font = FONT, bd = 0, pady = 0, padx = 4, justify = tk.LEFT,)
            self.elements['FORMAT_BOX_CUES'].grid(column = 1, row = 1, sticky = 'NEWS')
            self.elements['FORMAT_BOX_JSON'] = tk.Checkbutton(self.elements['FORMAT'])
            self.elements['FORMAT_BOX_JSON'].configure(variable = self.format_stamps, command=self.format_changed, 
                anchor = 'nw', font = FONT, bd = 0, pady = 0, padx = 4, justify = tk.LEFT,)
            self.elements['FORMAT_BOX_JSON'].grid(column = 2, columnspan=4, row = 1, sticky = 'NEWS')
            if DEBUG: print('SUBTITLES FORMAT: drawn')
        else:
            if DEBUG: print('SUBTITLES FORMAT: redrawn')
        self.elements['FORMAT'].configure(bg = COLOUR['FRAME_BG'],)
        self.elements['FORMAT_LABEL'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['FORMAT'],)
        self.elements['FORMAT_BOX_TEXT'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], command=self.format_changed, width = 4, 
            selectcolor = COLOUR['FRAME_BG'], activebackground = COLOUR['FRAME_BG'], text = TEXT['FORMATS'][0],
            activeforeground = COLOUR['TEXT_LABEL'],)
        self.elements['FORMAT_BOX_CUES'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], command=self.format_changed, width = 4, 
            selectcolor = COLOUR['FRAME_BG'], activebackground = COLOUR['FRAME_BG'], text = TEXT['FORMATS'][1], 
            activeforeground = COLOUR['TEXT_LABEL'],)
        self.elements['FORMAT_BOX_JSON'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], command=self.format_changed, width = 4, 
            selectcolor = COLOUR['FRAME_BG'], activebackground = COLOUR['FRAME_BG'], text = TEXT['FORMATS'][2], 
            activeforeground = COLOUR['TEXT_LABEL'],)

    def draw_language(self, e=None, *, redraw = False):
        if not redraw:
            self.elements['LANGUAGE'] = tk.Frame(self)
            self.elements['LANGUAGE'].configure(pady = self.padding,)
            for i in range(self.columns):
                self.elements['LANGUAGE'].columnconfigure(i, weight = 4)
            self.elements['LANGUAGE'].pack(side = tk.TOP, fill = tk.X, pady = 1, padx = 0)
            if DEBUG: print('SUBTITLES LANGUAGE: created')
            self.draw_language_elements()
        else:
            if DEBUG: print('SUBTITLES LANGUAGE: redrawn')
            self.draw_language_elements(redraw = redraw)
        self.elements['LANGUAGE'].configure(bg = COLOUR['FRAME_BG'],)

    def draw_language_elements(self, e=None, *, redraw = False):
        if not redraw:
            for widget in self.elements['LANGUAGE'].winfo_children():
                widget.destroy()
        if self.options_known:
            if not redraw:
                self.elements['LANGUAGE_LABEL'] = tk.Label(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_LABEL'].configure(anchor = 'nw', font = FONT, bd = 0, 
                    justify = tk.LEFT,)
                self.elements['LANGUAGE_LABEL'].grid(columnspan = self.columns, sticky = 'NEWS', pady = (0,8))
                ## "The Options Menu"
                self.elements['CHOICE'] = tk.Menubutton(self.elements['LANGUAGE'])
                self.elements['CHOICE'].configure(bd = 1, justify = tk.LEFT, anchor = 'w', font = FONT,
                    padx = 0, pady = 0, relief = tk.RAISED,)
                self.elements['CHOICE'].grid(column = 0, row = 1, sticky = 'EW', padx = (0,8), ipady = 4) 
                self.elements['CHOICE'].menu = tk.Menu(self.elements['CHOICE'])
                self.elements['CHOICE'].menu.configure(tearoff = 0, bd = 0, font = FONT)
                self.elements['CHOICE']['menu'] = self.elements['CHOICE'].menu
                for code, lang, text in self.possible_languages: # 1: the language code, 2: description and 3: both combined
                    self.clicked_languages.update({code: tk.IntVar()}) # new variable for every button, associated with the code through dict magic
                    self.elements['CHOICE'].menu.add_checkbutton(label = text,
                        variable = self.clicked_languages[code], command = self.update_selected_languages)
                ## plus translations
                self.elements['CHOICE_T'] = tk.Menubutton(self.elements['LANGUAGE'])
                self.elements['CHOICE_T'].configure(bd = 1, justify = tk.LEFT, anchor = 'w', font = FONT,
                    padx = 0, pady = 0, relief = tk.RAISED,)
                self.elements['CHOICE_T'].grid(column = 0, row = 2, sticky = 'EW', padx = (0,8), ipady = 4, pady = (4,0)) 
                self.elements['CHOICE_T'].menu = tk.Menu(self.elements['CHOICE_T'])
                self.elements['CHOICE_T'].menu.configure(tearoff = 0, bd = 0, font = FONT)
                self.elements['CHOICE_T']['menu'] = self.elements['CHOICE_T'].menu
##                if DEBUG:
##                    self.possible_translations = DEBUG_MENU
##                    print('OPTIONS_T: loaded hardcoded list')
                for code, lang, text in self.possible_translations: # 1: the language code, 2: description and 3: both combined
                    self.clicked_translations.update({code: tk.IntVar()}) # new variable for every button, associated with the code through dict magic
                    self.elements['CHOICE_T'].menu.add_checkbutton(label = text,
                        variable = self.clicked_translations[code], command = self.update_selected_languages)
                ## Selection
                self.elements['LANGUAGE_SELECTED'] = tk.Label(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_SELECTED'].configure(anchor = 'nw', font = FONT, bd = 0,
                        justify = tk.LEFT, textvariable = self.selection,)
                self.elements['LANGUAGE_SELECTED'].grid(columnspan = self.columns, row=3, sticky = 'NEWS', pady = (8,8))
                ## helpful buttons
                self.elements['LANGUAGE_CLEAR'] = tk.Button(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_CLEAR'].configure(bd = 1, command = self.clear_selection, font = FONT,
                    padx = 0, pady = 0,  relief = tk.RAISED, width = 9)
                self.elements['LANGUAGE_CLEAR'].grid(row = 1, column = self.columns, )
                self.elements['LANGUAGE_ALL'] = tk.Button(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_ALL'].configure(bd = 1, command = self.fill_selection, font = FONT,
                    padx = 0, pady = 0,  relief = tk.RAISED, width = 9)
                self.elements['LANGUAGE_ALL'].grid(row = 2, column = self.columns, pady=(4,0),)
                if DEBUG: print('SUBTITLES LANGUAGE OPTIONS: drawn')   ##########################
            else:
                if DEBUG: print('SUBTITLES LANGUAGE OPTIONS: redrawn') ########################
            self.elements['CHOICE'].configure(fg = COLOUR['TEXT'], activeforeground = COLOUR['TEXT'],
                bg = COLOUR['SELECT_BG'], activebackground = COLOUR['SELECT_BG_ACTIVE'], text = TEXT['LANGUAGE_OPTIONS'],)
            self.elements['CHOICE'].menu.configure(activeforeground = COLOUR['CHOICE_FG_ACTIVE'],fg = COLOUR['CHOICE_FG'],
                activebackground = COLOUR['CHOICE_BG_ACTIVE'], bg = COLOUR['CHOICE_BG'],)
            self.elements['CHOICE_T'].configure(fg = COLOUR['TEXT'], activeforeground = COLOUR['TEXT'],
                bg = COLOUR['SELECT_BG'], activebackground = COLOUR['SELECT_BG_ACTIVE'], text = TEXT['TRANSLATION_OPTIONS'],)
            self.elements['CHOICE_T'].menu.configure(activeforeground = COLOUR['CHOICE_FG_ACTIVE'],fg = COLOUR['CHOICE_FG'],
                activebackground = COLOUR['CHOICE_BG_ACTIVE'], bg = COLOUR['CHOICE_BG'],)
            self.elements['LANGUAGE_LABEL'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['LANGUAGE'],)
            self.elements['LANGUAGE_SELECTED'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'],)
            self.elements['LANGUAGE_CLEAR'].configure(fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['HELPERS'][0],
                activeforeground = COLOUR['ACTIVE'], activebackground = COLOUR['BUTTON_CLICKED'], highlightcolor = COLOUR['ACTIVE'],)
            self.elements['LANGUAGE_ALL'].configure(fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['HELPERS'][1],
                activeforeground = COLOUR['ACTIVE'], activebackground = COLOUR['BUTTON_CLICKED'], highlightcolor = COLOUR['ACTIVE'],)
            
        else:
            if not redraw:
                self.elements['LANGUAGE_LABEL'] = tk.Label(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_LABEL'].configure(anchor = 'nw', font = FONT, bd = 0, justify = tk.LEFT,)
                self.elements['LANGUAGE_LABEL'].grid(columnspan = self.columns, row=0, sticky = 'NEWS', pady = (0,8))
                self.elements['LANGUAGE_BUTTON'] = tk.Button(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_BUTTON'].configure(bd = 1, command = self.fetch_languages, width = 16, font = FONT,
                    padx = 0, pady = 0, relief = tk.RAISED,)
                self.elements['LANGUAGE_BUTTON'].grid(columnspan = 3, row = 1, sticky = 'NWS', pady = 3)
                self.elements['LANGUAGE_PADDING'] = tk.Label(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_PADDING'].configure(anchor = 'nw', )
                self.elements['LANGUAGE_PADDING'].grid(column = 0, row = 2, sticky = 'NEWS', pady = (4,4))
                self.elements['LANGUAGE_SELECTED'] = tk.Label(self.elements['LANGUAGE'])
                self.elements['LANGUAGE_SELECTED'].configure(anchor = 'nw', font = FONT, bd = 0, justify = tk.LEFT, textvariable = self.selection,)
                self.elements['LANGUAGE_SELECTED'].grid(columnspan = self.columns, row=3, sticky = 'NEWS', pady = (8,8))
                if DEBUG: print('SUBTITLES LANGUAGE ASK: drawn')
            else:
                if DEBUG: print('SUBTITLES LANGUAGE ASK: redrawn')
            self.selection.set(TEXT['DEFAULT_PARTIAL']+' de, en')
            self.elements['LANGUAGE_BUTTON'].configure(activebackground = COLOUR['BUTTON_CLICKED'], activeforeground = COLOUR['ACTIVE'],
                highlightcolor = COLOUR['ACTIVE'], fg = COLOUR['TEXT_BUTTON'], bg = COLOUR['BUTTON_NORMAL'], text = TEXT['OPTIONS'],)
            self.elements['LANGUAGE_SELECTED'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'],)
            self.elements['LANGUAGE_LABEL'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], text = TEXT['DEFAULTS'],)
            self.elements['LANGUAGE_PADDING'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'],)
        
    def draw_other(self, *, redraw = False):
        if not redraw:
            self.elements['BOTTOM'] = tk.Frame(self)
            self.elements['BOTTOM'].configure(pady = self.padding,)
            self.elements['BOTTOM'].columnconfigure(1, weight = 1, minsize=50)
            self.elements['BOTTOM'].pack(side = tk.TOP, fill = tk.BOTH, pady = (1, 0))
            self.elements['RUN'] = tk.Button(self.elements['BOTTOM'])
            self.elements['RUN'].configure(bd = 1, command = self.validate_and_run,  font = FONT,
                padx = 0, pady = 0, relief = tk.RAISED, width = 9,)
            self.elements['RUN'].pack(side = tk.RIGHT) 
            self.elements['STATUS'] = tk.Label(self.elements['BOTTOM'])
            self.elements['STATUS'].configure(font = FONT, bd = 0, textvariable = self.error,)
            self.elements['STATUS'].pack(side = tk.RIGHT, padx = (0,8))
            self.elements['BELOW'] = tk.Frame(self)
            self.elements['BELOW'].pack(side = tk.TOP, fill = tk.BOTH, expand = True)
            if DEBUG: print('SUBTITLES OTHER: drawn')
        self.elements['BOTTOM'].configure(bg = COLOUR['FRAME_BG'])
        self.elements['BELOW'].configure(bg = COLOUR['FRAME_BG'])
        self.elements['RUN'].configure(activebackground = COLOUR['BUTTON_CLICKED'], activeforeground = COLOUR['ACTIVE'],
                bg = COLOUR['BUTTON_NORMAL'], fg = COLOUR['TEXT_BUTTON'], highlightcolor = COLOUR['ACTIVE'], text = TEXT['EXTRACT'],)
        self.elements['STATUS'].configure(bg = COLOUR['FRAME_BG'], fg = COLOUR['TEXT_LABEL'], )

    ## The Functionality ################################################################################

    def kill(self, e=None):
        for widget in self.winfo_children():
            widget.destroy()
    def update_selected_languages(self, e=None):
        self.error.set('')
        i=0
        selection = TEXT['CHOSEN_PARTIAL']
        sorted_clicked_tuples = sorted(list(self.clicked_languages.items()))
        for code, clicked_var in sorted_clicked_tuples:
            if clicked_var.get() == 1:
                selection = selection + code if i==0 else selection + ', ' + code
                i+=1
        sorted_clicked_tuples = sorted(list(self.clicked_translations.items()))
        for code, clicked_var in sorted_clicked_tuples:
            if clicked_var.get() == 1 and code not in self.clicked_languages:
                selection = selection + code if i==0 else selection + ', ' + code
                i+=1
        if i==0:
            selection = selection + ' -- '
            if DEBUG: print('LANGUAGE: empty selection')
        self.selection.set(selection)
        if DEBUG: print('LANGUAGE: added or removed, label changed')

    def clear_selection(self, e=None):
        self.error.set('')
        for key in self.clicked_languages.keys():
            self.clicked_languages[key].set(0)
        self.selection.set(TEXT['CHOSEN_PARTIAL']+' -- ')
        if DEBUG: print('LANGUAGE: cleared selection')

    def fill_selection(self, e=None):
        self.error.set('')
        for key in self.clicked_languages.keys():
            self.clicked_languages[key].set(1)
        self.update_selected_languages()
        if DEBUG: print('LANGUAGE: filled selection')
                
    def getsaveplace(self, e=None):
        self.error.set('')
        self.outpath.set(filedialog.askdirectory())
        if DEBUG: print('PATH_DIALOGUE: opened and closed')

    def id_changed(self, e=None):
        self.error.set('')
        if self.options_known:
            self.options_known = False
            self.transcript_list = None
            self.draw_language_elements()
            self.possible_languages = []
            self.selection.set(TEXT['DEFAULT_PARTIAL']+' de, en')
            self.draw_language_elements()
        if DEBUG: print('ID: changed')

    def format_changed(self, e=None):
        self.error.set('')
        if DEBUG: print('FORMAT: changed')

    def path_changed(self, e=None):
        self.error.set('')
        if DEBUG: print('PATH: changed')

    def fetch_languages(self, e=None):
        self.error.set('')
        video_id = self.extract_id()
        if video_id is None:
            if DEBUG: print('FETCH: url_field empty or wrong: ', self.error.get())
            return
        try:
            self.transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            ## This is kind of a hack... TranscriptList comes from the API and it's only __function__ is __iter__, so I had to make do!
            if sum(1 for x in self.transcript_list) == 0: raise IOError('Zero transcripts available.')
        except IOError as e:
            if DEBUG: print('FETCH: ', e)
            self.error.set(ERR['BROKEN'])
            return
        except Exception as e:
            if DEBUG: print('FETCH: EXCEPTION: ', e)
            self.error.set(ERR['BROKEN']) 
            return
        ## LANGUAGES
        temp_possible_languages = []
        for transcript in self.transcript_list:
            temp_possible_languages.append((transcript.language_code,
                                            transcript.language,
                                            ''.join((transcript.language_code, ' (', transcript.language, ')'))))
        temp_possible_languages.sort()
        for lang_tuple in temp_possible_languages:
                self.possible_languages.append(lang_tuple)
        if DEBUG:
            assert(len(temp_possible_languages) ==  len(self.possible_languages)), f'fetch_languages broke, orig:{temp_possible_languages}, after:{self.possible_languages}'
        ## TRANSLATIONS
        temp_possible_translations = []
        for transcript in self.transcript_list._translation_languages:
            temp_possible_translations.append((transcript['language_code'],
                                               transcript['language'],
                                               ''.join((transcript['language_code'], ' (', transcript['language'], ')'))))
        temp_possible_translations.sort()
        for lang_tuple in temp_possible_translations:
                self.possible_translations.append(lang_tuple)
        if DEBUG:
            assert(len(temp_possible_translations) ==  len(self.possible_translations)), f'fetch_languages broke, orig:{temp_possible_translations}, after:{self.possible_translations}'
        self.options_known = True
        self.update_selected_languages()
        self.draw_language_elements()

    def extract_id(self, e=None):
        self.error.set('')
        try:
            url_or_id = self.url_field.get()
            if len(url_or_id) < 1:
                self.error.set(ERR['INVALID'])
                return None
            elif 10 < len(url_or_id) < 14:
                video_id    = url_or_id
                if DEBUG: print('ID: id')
            elif 'youtu.be' in url_or_id:
                tail            = url_or_id.split('.be/')[1]
                video_id        = tail.split('?')[0]
                if DEBUG: print('ID: short')
            elif 'youtube' in url_or_id:
                if DEBUG: print('ID: long')
                if ('/watch?' in url_or_id):
                    tail        = url_or_id.split('/watch?')[1]
                else:
                    tail        = url_or_id.split('/v/')[1]
                tail        = tail.split('&')[0]
                video_id    = tail.split('v=')[1]
            else:
                if DEBUG: print('ID: none of the above')
                self.error.set(ERR['UNRECOGNIZABLE'])
                return None
            if DEBUG: print('ID: SUCCESS: ', video_id)
            return video_id
        except Exception as e:
            if DEBUG: print('ID: EXCEPTION: ', e)
            self.error.set(ERR['UNRECOGNIZABLE'])
            return None
        return None
        
    def validate_and_run(self, e=None):
        self.error.set('')
        video_id = self.extract_id()
        if DEBUG: print('RUN: ', video_id)
        if video_id is None:
            return
        if '/' in self.outpath.get() or ':' in self.outpath.get():
            self.path = self.outpath.get()
            self.filename = video_id
        else:
            self.error.set(ERR['PATH'])
            if DEBUG: print('RUN: no / found in path')
            return

        if self.format_text.get() + self.format_stamps.get() + self.format_json.get() < 1:
            self.error.set(ERR['FORMAT'])
            if DEBUG: print('RUN: no format selected')
            return

        selection = ['de', 'en']
        options_available = self.options_known and len(self.clicked_languages)+len(self.clicked_translations) > 0
        if options_available:
            selection = []
            sorted_clicked_tuples = sorted(list(self.clicked_languages.items()))
            for code, clicked_var in sorted_clicked_tuples:
                if clicked_var.get() == 1:
                    selection.append(code)
            sorted_clicked_tuples = sorted(list(self.clicked_translations.items()))
            for code, clicked_var in sorted_clicked_tuples:
                if clicked_var.get() == 1 and code not in selection:
                    selection.append(code)
            if DEBUG: print('RUN: codes to be fetched: ', selection)
        else:
            if DEBUG: print('RUN: fallback on default codes')
            self.fetch_languages()
        fetched_one = False
        found_status = []
        not_found_status = []
        for code in selection:
            try:
                transcript = self.transcript_list.find_transcript([code])
                cue_dict_list = transcript.fetch()
                if self.format_text.get()==1:
                    save_as_text(cue_dict_list, video_id, self.outpath.get(), code)
                if self.format_stamps.get()==1:
                    save_as_cues(cue_dict_list, video_id, self.outpath.get(), code)
                if self.format_json.get()==1:
                    save_as_json(cue_dict_list, video_id, self.outpath.get(), code)
                fetched_one = True
                found_status.append(code)
                if len(found_status) == 1:
                    self.master.receive_transcript_data(cue_dict_list, video_id, self.outpath.get(), code)
            except Exception as e:
                if DEBUG: print('RUN: EXCEPTION B: ', e)
                not_found_status.append(code)
                continue
        for code in sorted(not_found_status):
            try:
                if 'en' in self.possible_languages:
                    transcript = self.transcript_list.find_transcript(['en'])
                elif len(found_status)>0:
                    transcript = self.transcript_list.find_transcript([found_status[0]])
                else:
                    transcript = self.transcript_list.find_transcript([possible_languages[0][0]])
                cue_dict_list = transcript.translate(code).fetch()
                if self.format_text.get()==1:
                    save_as_text(cue_dict_list, video_id, self.outpath.get(), code, is_translation=True)
                if self.format_stamps.get()==1:
                    save_as_cues(cue_dict_list, video_id, self.outpath.get(), code, is_translation=True)
                if self.format_json.get()==1:
                    save_as_json(cue_dict_list, video_id, self.outpath.get(), code, is_translation=True)
                fetched_one = True
                found_status.append(code)
                if len(found_status) == 1:
                    self.master.receive_transcript_data(cue_dict_list, video_id, self.outpath.get(), code)
                if code in not_found_status: not_found_status.remove(code)
            except Exception as e:
                if DEBUG: print('RUN: EXCEPTION C: ', e)
                continue 
        if not fetched_one:
            if options_available:
                self.error.set(ERR['ZERO_CHOSEN'])
            else:
                self.error.set(ERR['DEFAULT_UNSUCCESSFUL'])
            return
        if len(not_found_status) > 0:
            self.error.set(ERR['ONLY_FOUND_PARTIAL'] + str(found_status)[1:-1])
        else:
            self.error.set(ERR['SUCCESS'])
        display_transcript_using_received_transcript_data()

#### GLOBAL FUNCTIONS, DATA, MAIN #######################################################################

def save_as_text(cues, video_id, path, language, is_translation=False):
    translated = '_translation' if is_translation else ''
    try:
        with open(''.join((path, '/', video_id, '_', language, '_text', translated, '.txt')), 'w') as file:
            for cue in cues:
                file.write(cue['text'].replace('\n', ' ') + ' ')
    except Exception as e:
        if DEBUG: print('SAVE: TEXT: EXCEPTION: ', e)
def save_as_cues(cues, video_id, path, language, is_translation=False):
    translated = '_translation' if is_translation else ''
    try:
        with open(''.join((path, '/', video_id, '_', language, '_cues', translated, '.txt')), 'w') as file:
            for cue in cues:
                line = ''.join((str(cue['start']), ', ', str(cue['duration']), '\n', str(cue['text']), '\n'))
                file.write(line)
    except Exception as e:
        if DEBUG: print('SAVE: CUES: EXCEPTION: ', e)
def save_as_json(cues, video_id, path, language, is_translation=False):
    translated = '_translation' if is_translation else ''
    try:
        with open(''.join((path, '/', video_id, '_', language, translated, '.json')), 'w') as file:
            json.dump(cues, file)
    except Exception as e:
        if DEBUG: print('SAVE: JSON: EXCEPTION: ', e)

def lerp(a, b, t):
    return a*(1-t) + b*(t)
def colour_to_tuple(colour):
    return tuple([int(c, 16) for c in [colour[1:3], colour[3:5], colour[5:7]]])
def tuple_to_colour(tupple):
    return ''.join(('#', *[hex(c)[2:].zfill(2) for c in tupple]))
def mix_colours(colour1, colour2, by_how_much):
    return tuple_to_colour(tuple([int(lerp(a, b, by_how_much)) for a, b in zip(colour_to_tuple(colour1), colour_to_tuple(colour2))]))

COLOUR = {}
COLOURS = {'DARK': {}, 'LIGHT': {}}
## DARK
COLOURS['DARK']['FRAME_BG'] = '#111111'
COLOURS['DARK']['FRAME_BG_CONTRAST'] = '#333333'
COLOURS['DARK']['TEXT'] = '#ffffff'
COLOURS['DARK']['TEXT_LABEL'] = '#ffffff'
COLOURS['DARK']['BUTTON_NORMAL'] = '#b25c11'
COLOURS['DARK']['BUTTON_CLICKED'] = '#ef760b'
COLOURS['DARK']['ACTIVE'] = '#444444'
COLOURS['DARK']['ENTRY_BG'] = '#222222'
COLOURS['DARK']['TAB_OFF'] = mix_colours('#111111', '#ef760b', .3)
COLOURS['DARK']['TEXT_BUTTON'] = '#ffffff'
COLOURS['DARK']['CHOICE_BG_ACTIVE'] = '#222222'
COLOURS['DARK']['CHOICE_FG_ACTIVE'] = '#ef760b'
COLOURS['DARK']['CHOICE_BG'] = '#111111'
COLOURS['DARK']['CHOICE_FG'] = '#ffffff'
COLOURS['DARK']['SELECT_BG'] = '#222222'
COLOURS['DARK']['SELECT_BG_ACTIVE'] = '#333333'
## LIGHT
COLOURS['LIGHT']['FRAME_BG'] = '#eeeeee'
COLOURS['LIGHT']['FRAME_BG_CONTRAST'] = '#7f7f7f'
COLOURS['LIGHT']['TEXT'] = '#000000'
COLOURS['LIGHT']['TEXT_LABEL'] = '#000000'
COLOURS['LIGHT']['BUTTON_NORMAL'] = '#006AB3'
COLOURS['LIGHT']['BUTTON_CLICKED'] = '#0097f9'
COLOURS['LIGHT']['ACTIVE'] = '#444444'
COLOURS['LIGHT']['ENTRY_BG'] = '#cccccc'
COLOURS['LIGHT']['TAB_OFF'] = mix_colours('#eeeeee', '#0097f9', .3)
COLOURS['LIGHT']['TEXT_BUTTON'] = '#ffffff'
COLOURS['LIGHT']['CHOICE_BG_ACTIVE'] = '#444444'
COLOURS['LIGHT']['CHOICE_FG_ACTIVE'] = '#0097f9'
COLOURS['LIGHT']['CHOICE_BG'] = '#aaaaaa'
COLOURS['LIGHT']['CHOICE_FG'] = '#000000'
COLOURS['LIGHT']['SELECT_BG'] = '#cccccc'
COLOURS['LIGHT']['SELECT_BG_ACTIVE'] = '#bbbbbb'
## SELECT INITIAL
COLOUR.update(COLOURS['DARK'])

FONT = ('Helvetica' , 13)

TEXTS = {'EN': {}, 'DE': {}}
TEXT = {}
TEXTS['EN'].update({
    'TITLE': 'Subtitle Extractor',
    'EXPLAIN': 'To edit the subtitles in here, either:\n - download them to the left or\n - load them from a text file:',
    'B_LOAD_FILE': 'Load a text file...',
    'URL_INPUT': 'Please provide the YouTube URL or the video ID:',
    'OUTPUT': 'Where should the output go? (optional)',
    'CHOOSE': 'Choose...',
    'FORMAT': 'What format should the subtitles be in?',
    'FORMATS': ['Text', 'JSON', 'Timestamped'],
    'LANGUAGE': 'What language should the subtitles be in?',
    'LANGUAGE_OPTIONS': ' These are your language options:',
    'TRANSLATION_OPTIONS': ' These are your translation options:',
    'HELPERS': ['Clear all', 'Select all'],
    'DEFAULTS': 'Languages - try the default or see what\'s possible:',
    'OPTIONS': 'Ask for options',
    'EXTRACT': 'Extract',
    'CHOSEN_PARTIAL': 'Chosen: ',
    'DEFAULT_PARTIAL': 'Default: ',
    'TOOL_SPELL': 'Choose a language for spell-\nchecking, then press start:',
    'TOOL_SPELL_B': 'Start spellchecking',
    'TOOL_SAVE': 'Save the text:',
    'TOOL_SAVE_B': 'Save...',
    'TOOL_SPEECH': 'Text-to-speech the selected text:',
    'TOOL_SPEECH_B': 'Read it!',
    'SPEECH_UNAVAILABLE': 'Couldn\'t find TTS capabilities...',
    'TOOL_DEFAULT_DICT': 'Choose a language option:',
})
TEXTS['DE'].update({
    'TITLE': 'Untertitel Extrahierer',
    'EXPLAIN': 'Um hier die Untertitel zu bearbeiten,\n - lade sie links herunter oder\n - lade eine Textdatei:',
    'B_LOAD_FILE': 'Öffne Textdatei...',
    'URL_INPUT': 'Bitte gebe eine Video-ID oder die ganze URL ein:',
    'OUTPUT': 'Wo sollen sie gespeichert werden? (optional)',
    'CHOOSE': 'Öffne...',
    'FORMAT': 'In welchem Format sollen sie gespeichert werden?',
    'FORMATS': ['Text', 'JSON', 'Zeitstempel'],
    'LANGUAGE': 'Welche Sprachen sollen heruntergeladen werden?',
    'LANGUAGE_OPTIONS': ' Dies sind die Sprachoptionen:',
    'TRANSLATION_OPTIONS': ' Dies sind mögliche Übersetzungen:',
    'HELPERS': ['Alle entfernen', 'Alle wählen'],
    'DEFAULTS': 'Sprachen - auf gut Glück oder nach Anfrage:',
    'OPTIONS': 'Anfragen',
    'EXTRACT': 'Extrahiere',
    'CHOSEN_PARTIAL': 'Auswahl: ',
    'DEFAULT_PARTIAL': 'Standard: ',
    'TOOL_SPELL': 'Wähle eine Sprache um die \nRechtschreibung zu prüfen:',
    'TOOL_SPELL_B': 'Rechtschreibprüfung',
    'TOOL_SAVE': 'Text speichern:',
    'TOOL_SAVE_B': 'Speichern...',
    'TOOL_SPEECH': 'Markierten Text vorlesen lassen:',
    'TOOL_SPEECH_B': 'Vorlesen, bitte!',
    'SPEECH_UNAVAILABLE': 'Konnte keine Stimme finden...',
    'TOOL_DEFAULT_DICT': 'Sprache wählen:',
})
TEXT.update(TEXTS['EN'])

ERRS = {'EN': {}, 'DE': {}}
ERR = {}
ERRS['EN'].update({
    'SUCCESS': 'Success, all transcripts downloaded!',
    'NONE_FOUND': 'Zero transcripts found for this video.',
    'BROKEN': 'Either your URL/ID is broken, or the API',
    'INVALID': 'Please enter a video URL or an ID at the top',
    'UNRECOGNIZABLE': 'The URL/ID is not recognizable, please double-check.',
    'PATH': 'Please specify a valid output path',
    'FORMAT': 'Please specify at least one format',
    'ZERO_CHOSEN': 'Please select at least one language option',
    'DEFAULT_UNSUCCESSFUL': 'Neither German nor English could be aquired, they might not be available',
    'ONLY_FOUND_PARTIAL': 'Only found and downloaded: ',
})
ERRS['DE'].update({
    'SUCCESS': 'Erfolg, alles heruntergeladen!',
    'NONE_FOUND': 'Für dieses Video existieren keine Transkripte',
    'BROKEN': 'Entweder deine URL/ID ist kaputt, oder die API',
    'INVALID': 'Bitte gebe ganz oben eine URL oder Video-ID ein',
    'UNRECOGNIZABLE': 'URL/ID kann nicht erkannt werden, bitte korrigieren',
    'PATH': 'Der Pfad konnte nicht gefunden werden',
    'FORMAT': 'Es wurde kein Format gewählt',
    'ZERO_CHOSEN': 'Es wurde keine Sprache gewählt',
    'DEFAULT_UNSUCCESSFUL': 'Weder Deutsch noch Englisch konnte gefunden werden',
    'ONLY_FOUND_PARTIAL': 'Konnte nur diese finden: ',
})
ERR.update(ERRS['EN'])

def main():
    root = Root()
    root.mainloop()

if __name__  ==  '__main__':
    main()






















