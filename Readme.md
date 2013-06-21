## [HandyTabs](https://github.com/travmik/HandyTabs)
## Overview

Handy Tabs is a [Sublime Text 2](http://www.sublimetext.com/2) plugin that helps you to keep you tabbar in order.

How often do you see something like this?
![FFFFUUUUUU](http://i.piccy.info/i7/35edbf83382b2225c7d84eac35ceef83/4-60-516/9482149/FFFFFFFFUUUUUUUUUUUUUUUU_env_2013_06_07_20_19_58.jpg) 

Now it stops!
Now you 

## Installation
To install this plugin, you have two options:

1. If you have [Sublime Package Control](http://wbond.net/sublime_packages/package_control) installed, simply search for `HandyTabs` to install.

2. Clone source code to Sublime Text packages folder *Sublime Text 2/Packages*.

*OSX*
```shell
cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
git clone git://github.com/travmik/HandyTabs.git
```

*Ubuntu*
```shell
cd ~/.config/sublime-text-2/Packages
git clone git://github.com/travmik/HandyTabs.git
```

*Windows*
```dos
cd "%APPDATA%\Sublime Text 2\Packages"
git clone git://github.com/travmik/HandyTabs.git
```


## Settings

There are only one settings that control Handy Tabs behavior:

* __open\_tab_limit__: Controls the maximum allowed number of tabs. Note that dirty tabs are not count towards this limit. The default is 10.

To change these settings update `handytabs.sublime-settings`.

	{
    	"open_tab_limit"   :  10
	}
