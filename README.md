# 🧪 Rick Assistant ZSH Plugin

A Rick Sanchez-themed ZSH plugin that brings the multiverse of Rick and Morty into your terminal experience. Complete with portal animations, sarcastic remarks, and inter-dimensional adventures, this plugin turns your boring terminal into a scientific playground that would make even the smartest man in the universe proud.


⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢰⠀⢀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢲⠶⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠁⠀⠈⣍⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⡄⠈⠑⠢⢄⡀⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⣀⣤⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠠⢵⠀⠀⠀⠀⠈⠓⠤⣤⠄⡼⠀⠀⠀⠀⠀⠘⣿⣿⣿⠤⠄⠀⣠⠴⠊⢡⣿⠀⠠⠤⣤⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⠈⠲⠃⠀⠀⠀⠀⠀⠀⢻⣿⡿⠗⠒⠉⠀⠀⠀⣾⣏⣠⣴⣾⡏⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⠀⢀⡠⠤⠔⠒⠂⠤⠄⣈⠁⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⡤⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⢄⠀⠀⠀⠀⣼⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀
⠔⡀⠉⠉⠉⠉⠈⠉⠉⠉⠀⢀⠎⠀⠀⠀⠀⣀⠤⢒⡠⠖⠂⠀⣀⣀⣀⠱⡀⠀⠀⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠑⣤⡀⠀⠀⠀⠀⠀⠀⠀⡎⠀⠀⠠⠄⠋⠒⢈⡠⠄⠒⣈⠡⠤⠐⠚⠁⠙⡄⠀⠙⠛⠛⠻⢿⡶⠓⢶⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠙⢢⡀⠀⠀⠀⠀⢰⢁⡤⠐⠒⠒⢊⣉⡠⠔⠚⠉⡀⠀⠀⠀⠈⠒⢄⠰⡀⠀⠀⠀⣠⠞⢀⣴⣯⣅⣀⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠓⠤⡀⠀⠀⢸⠈⢉⠁⠉⠉⠀⠉⠢⡀⠀⡘⠀⢀⣀⣠⡤⠀⠘⢇⢣⠀⠀⣴⣭⣶⣿⣿⣿⣿⣿⡿⠟⠁
⠀⠀⠀⠀⠀⠀⠀⣀⠼⠃⠀⢸⣠⠃⠀⠀⠀⣀⡠⠤⠼⡀⢻⠉⠁⠀⠉⠀⠀⠀⡼⠸⡀⠀⠈⠻⢿⣿⣿⣿⠟⠉⠀⠀⠀
⠀⠀⢠⣠⠤⠒⠊⠁⠀⠀⠀⠈⡏⡦⠒⠈⠙⠃⠀⠀⢠⠇⠈⠢⣀⠀⠀⠀⣀⠔⠁⠀⣇⠀⠀⠀⢀⡽⠛⣿⣦⣀⡀⠀⠀
⠀⠀⠀⠈⠑⠢⢄⡀⠀⠀⠀⠀⢇⠘⢆⡀⠀⠀⢀⡠⠊⡄⠀⢰⠀⠉⠉⠉⣠⣴⠏⠀⣻⠒⢄⢰⣏⣤⣾⣿⣿⣿⣦⣄⠀
⠀⠀⠀⠀⠀⠀⠙⢻⣷⣦⡀⠀⢸⡀⠀⡈⠉⠉⢁⡠⠂⢸⠀⠀⡇⠙⠛⠛⠋⠁⠀⠀⣿⡇⢀⡟⣿⣿⣿⣿⣿⣿⠟⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠇⠀⡴⠇⠀⠈⠉⠉⠀⠀⠀⠀⢣⣠⠇⠀⠀⠀⠀⠀⠀⠀⣿⣿⡟⠀⢻⠻⣿⡟⠉⠉⠉⠁⠀
⠀⠀⠀⠀⠀⠀⢀⡠⠖⠁⠀⢸⠀⠘⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⠐⢶⣿⢷⣯⣭⣤⣶⣿⣿⣦⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠒⠛⠒⠒⠤⠤⢲⠑⠦⢧⠀⠀⠀⠀⢀⡤⢖⠂⠉⠉⡸⠁⠀⠀⠀⢀⣾⣾⠈⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠾⣿⠀⠀⠈⢆⠸⣄⠊⠁⠀⠀⡉⢆⠀⡆⣀⠀⠀⠀⣰⢿⣷⣶⣾⣿⣿⣏⠉⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠼⠠⠴⢞⣿⢦⠀⠀⠀⠀⠀⠛⠀⠉⠁⠛⠃⢀⣴⣿⣾⣿⣿⣿⣿⡿⠿⠆⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣶⡷⢄⡀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⣿⠷⡖⠢⠤⠔⠒⠻⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⢉⡩⢽⢻⠗⠤⢀⣀⣀⡠⢿⣿⣿⠿⣏⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠊⠁⢠⠊⣸⠀⠀⠀⠀⠀⠀⠀⢻⠈⢖⠂⢉⠒⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀


## 🚀 Features

- **Ricktastic Menu System**: Navigate through dimensions with a sleek, portal-themed menu system
- **System Monitoring**: Keep track of your system's health with temperature alerts and resource monitoring
- **Powerlevel10k Integration**: Enhance your Powerlevel10k prompt with Rick-themed segments
- **Rick-ified Terminal**: Enjoy sarcastic, dismissive responses in pure Rick Sanchez style
- **Multiple Implementation Options**: Choose between Python and pure ZSH implementations

## 📦 Requirements

- ZSH (5.8 or newer)
- Oh My ZSH
- Powerlevel10k
- Python 3

## 💾 Installation

### Using Oh My ZSH

1. Clone this repository into your Oh My ZSH custom plugins directory:

```bash
git clone https://github.com/mmadalone/rick_assistant.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/rick_assistant
```

2. Add `rick_assistant` to your plugins array in your `.zshrc` file:

```bash
plugins=(... rick_assistant)
```

3. Source your `.zshrc` file:

```bash
source ~/.zshrc
```

4. Run the setup wizard (optional):

```bash
rick_assistant_setup
```

## 🔧 Usage

### Basic Commands

- `rick help` - Display help information
- `rick menu` - Open the Ricktastic menu
- `rick status` - Show system status
- `rick quote` - Get a random Rick quote
- `rick config` - Configure plugin settings

### Menu Navigation

The Ricktastic menu offers an intuitive interface to access all plugin features:

- Use arrow keys or numbers to navigate
- Press Enter to select
- Press ESC to go back
- Press Q to quit

### Powerlevel10k Integration

Add the Rick segment to your Powerlevel10k prompt by adding `rick_segment` to your `POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS` in your `.p10k.zsh` file:

```bash
POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS+=(rick_segment)
```

## ⚙️ Configuration

Configure Rick Assistant using the configuration menu:

```bash
rick config
```

Or edit the configuration file directly:

```bash
$EDITOR ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/rick_assistant/config/rick_assistant.conf
```

### Key Configuration Options

- **Menu Style**: Choose between different menu border styles
- **Portal Animations**: Enable/disable typing animations
- **System Monitoring**: Configure temperature thresholds and alerts
- **Implementation**: Choose between Python and pure ZSH implementations
- **Rick's Attitude**: Adjust how sarcastic Rick's responses are

## 🛠️ Development Status

The Rick Assistant ZSH Plugin is currently at **65%** completion:

- Phase 1 (Core Foundation): **100%** complete ✅
- Phase 2 (ZSH Integration): **100%** complete ✅
- Phase 3 (Enhanced UI & Experience): **85%** complete 🔄
- Phase 4 (Command Processing & Safety): **45%** complete 🔄
- Phase 5 (Expanded Rick Features): **25%** complete 🔄
- Phase 6 (AI Integration): **10%** complete 🟡
- Phase 7 (Advanced Features): **5%** complete 🟡

## 📝 Contributing

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request

Please make sure your code follows the project's coding style and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The creators of Rick and Morty for the inspiration
- The ZSH and Oh My ZSH communities
- The Powerlevel10k project
- AI cause I can't code for shit. You can tell!
- My homie Arden. He knows why.
- My homie Sebastian. He sure as fuck knows why.
- Yomama.
---

*"Wubba lubba dub dub!"* - Madalone

> **Note**: This project is a fan creation and not affiliated with Adult Swim, Rick and Morty, or its creators but it sure wishes it was. Some of them anyway.
