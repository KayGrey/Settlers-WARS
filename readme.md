# ⚔️ Settler Wars: Dark Lord Edition

> *Gather resources. Build your fortress. Destroy the Shadow Beasts. Claim glory.*

A fast-paced 2D single-player survival game built with Python and Pygame. You play as the **Dark Lord**, defending your realm against two relentless **Shadow Beasts** that gather, build, and hunt you down.

---

## 🎮 Gameplay

| Resource | Purpose |
|---|---|
| 🪵 **Wood** | Build **Walls** and **Houses** |
| 🪨 **Stone** | Build **Towers** and boost **Attack Power** (+2 dmg per stone, max +20) |

| Building | Cost | Effect |
|---|---|---|
| Wall | 2 Wood | Blocks enemy movement |
| House | 4 Wood | Increases your max HP by 20 |
| Tower | 3 Stone | Auto-attacks nearby enemies |

### 🏆 Win & Lose
- **WIN** — Destroy both Shadow Beasts
- **LOSE** — Your HP reaches 0

---

## 🕹️ Controls

| Key | Action |
|---|---|
| `Arrow Keys` | Move |
| `F` | Gather resource / Build |
| `G` | Attack |
| `R` | Restart (after game ends) |
| `ESC` | Quit |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Pygame

### Installation

```bash
# Clone the repository
git clone https://github.com/KayGrey/settler-wars.git
cd settler-wars

# Install dependencies
pip install -r requirements.txt

# Run the game
python settler_wars.py
```

---

## 📁 Project Structure

```
settler-wars/
│
├── settler_wars.py       # Main game file
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── LICENSE               # MIT License
└── .gitignore            # Git ignore rules
```

---

## 💡 Strategy Tips

- Gather **4 Wood** first → build a **House** to boost your HP
- Collect **3 Stone** → build a **Tower** to fight for you passively
- Stockpile **Stone** to maximise your attack damage before engaging
- Use **Walls** to funnel and slow Shadow Beasts while your Tower chips them down

---

## 🛠️ Built With

- [Python 3](https://www.python.org/)
- [Pygame](https://www.pygame.org/)

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request
