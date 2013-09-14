## [ZenTabs](https://github.com/travmik/ZenTabs)
## Overview  
Zen Tabs is a [Sublime Text 2](http://www.sublimetext.com/2) plugin that helps you to keep you tab bar in Zen.  
How often do you see something like this?
![FFFFUUUUUU](https://dl.dropboxusercontent.com/u/22258694/ZenTabs/ZenTabs-FFUUU.jpg)  
Now it stops!  
Now you can be in Zen when you working with Sublime Text.

Your tab bar can always have a look like this:
![Zen](https://dl.dropboxusercontent.com/u/22258694/ZenTabs/ZenTabs-10.jpg)  
Or even like this:  
![Zeeeeeeeeen](https://dl.dropboxusercontent.com/u/22258694/ZenTabs/ZenTabs-Zen.jpg)  
You have to do nothing for this. You just need to install this package, set opened tabs limit(default 10) and enjoy. 
When you will open 11th tab the oldest one will be closed.

## Installation
To install this plugin, you have two options:  
1. If you have [Sublime Package Control](http://wbond.net/sublime_packages/package_control) installed, simply search for `Zen Tabs` to install.  
2. Clone source code to Sublime Text packages folder *Sublime Text 2/Packages*.  
3. Download archive with the latest [release](https://github.com/travmik/ZenTabs/releases) and unpack it to Sublime Text packages folder *Sublime Text 2/Packages*.  

*OSX*

    cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
    git clone git://github.com/travmik/ZenTabs.git
  
*Linux*

    cd ~/.config/sublime-text-2/Packages
    git clone git://github.com/travmik/ZenTabs.git

*Windows*

    cd "%APPDATA%\Sublime Text 2\Packages"
    git clone git://github.com/travmik/ZenTabs.git

## Key bindings
`Preferences > Package Settings > Zen Tabs > Key Bindings`  
`alt+shif+r` - reload settings without restarting sublime  
`alt+tab` - show quick panel with opened tabs  

## Settings
`Preferences > Package Settings > Zen Tabs > Settings`  
* __open_tab_limit__: Controls the maximum allowed number of tabs. 
Note that edited or draft tabs are not count towards this limit. The default is 10.  
* __highlight_modified_tabs__: Makes tabs with modified files more visible. True by default.   
* __show_full_path__: Show full path to file in quick panel. False by default. Zennn....  
After editing don't forget to press `alt+shift+r` to reload settings.

## Quick panel
When you click `alt+tab`(default - can be changed in key-binding) Quick Panel with opened tabs will be opened:
![Quick Panle](https://dl.dropboxusercontent.com/u/22258694/ZenTabs/ZenTabs-QuickPanel.jpg)
* you can proceed to push `alt+tab` and move through tabs
* you can use arrow keys to move through tabs
* you can start typing name of tab to filter items in panel

## Features and improvements
[Todo](TODO.todo)

## Contribution
You can contribute on [github](https://github.com/travmik/ZenTabs).    
We always welcome pull requests. Here's some general rules for pull requests be accepted:  
- [PEP8](http://www.python.org/dev/peps/pep-0008/) is our coding style guide.   
- Please create a branch before sending pull requests.   
- Your pull request should be atomic. That is, fix a bug or implementing a feature in one commit instead of multiple commit.    This is a recommendation, not a requirement.   

Copyright 2011-2013 [Stanislav Parfeniuk](http://www.linkedin.com/in/stanislavparfeniuk). Licensed under the MIT License
