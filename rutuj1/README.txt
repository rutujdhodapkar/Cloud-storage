♟️ Chess AI Web App - AI-Powered Chess Analysis  

 Overview  
This project is an advanced AI-driven chess web application that leverages deep learning for intelligent move prediction, with minimal reliance on Stockfish. Unlike traditional chess engines that rely purely on brute-force calculations, this AI model predicts human-like, strategic moves based on patterns learned from millions of master-level games.  

The application supports real-time move analysis, intelligent move recommendations, and game tracking, providing users with an interactive and engaging chess experience. 

To run the project- just run app.py file. 

to tun this project u will need to be a authorize person.

---

 Key Features  

✔ AI-Powered Move Predictions – Deep learning model suggests the best next move based on game history.  
✔ Real-Time Move Analysis – AI evaluates each move dynamically and provides feedback.  
✔ Stockfish as a Secondary Validator – Used only for verifying AI-generated moves.  
✔ Move History Tracking – Saves and loads previous games for review.  
✔ User Authentication – Secure login and session management.  
✔ WebSockets for Instant Move Updates – Enables real-time game interaction.  

---

 Technology Stack  

 Backend:  
- Flask – Web framework  
- Flask-SocketIO – Real-time WebSocket communication  
- Python-Chess – Board state handling  
- PyTorch / TensorFlow – Deep learning model for move prediction  

 Frontend:  
- HTML, CSS, JavaScript – UI/UX components  
- WebSockets (Socket.IO) – Real-time game updates  

 Data Storage:  
- JSON – Move history storage  
- CSV – User authentication data  

---

 How the AI Works  

 Deep Learning Model for Move Prediction  
- Trained on a dataset of 70+ million master-level games  
- Utilizes a neural network to predict the most probable move  
- Analyzes opening theory, middlegame tactics, and endgame strategies  
- Unlike Stockfish, it emulates human decision-making rather than brute-force calculations  

 Stockfish as a Secondary Verification Tool  
- Validates the AI-generated moves to ensure legality and optimality  
- Computes alternative suggestions when necessary  

This hybrid approach provides a balance between human-like strategic play and computational accuracy.  

---

 Project Structure  
--------------------------------------------------------------------
/📂project_root/
│
│── app.py
│── deepanalysis.py
│── main.py
│── model.py
├── move_predictor.pth (optional)
├── processed_dataset.csv (optional)
├── stockfishmodl.py
├── movest.txt (optional)
├── README.txt (optional)
├── requirements.txt (optional)
│
│
│── 📂stockfish/
│      |── stoskfish.exe
│
│
│── 📂template/
│      ├── home.html
│      ├── login.html
│      ├── index.html
│      ├── contact.html
│      ├── deepthhome.html
│      ├── error.html
│      ├── results.html
│      ├── data.csv
│      │── 📂static/
│             ├── move.json (optional)
│             ├── desktop.png
│             ├── mobile.png
│             ├── homesmall.png
│             ├── home.png
│             ├── stockfish-windows-x86-64-avx2.exe 
--------------------------------------------------------------------



to tun this project u will need to be a authorize person.

---

 Installation & Setup  

 1. Install Dependencies  

Ensure you have Python installed, then run:  

```sh
pip install -r requirements.txt

 2. Run the Application
python app.py


install all packages, and just run app.py code,
to tun this code you will need python 12.9 or letter installed.

 Usage Guide
 Game Interface
- Sign up or log in to start playing.

- Make a move on the interactive chessboard.

- AI will analyze and suggest the best move based on learned patterns.

 Stockfish will verify (if necessary) to ensure accuracy.

 Track game history and review past moves.
to tun this project u will need to be a authorize person.

 License
- This project is released under the MIT License.

- For contributions, feel free to submit pull requests or report issues.

- to tun this project u will need to be a authorize person.

 Developed by: Rutuj Dhodapkar, Om Shelke, Anurag Vaishnav, Vishal Patil.

 Rutuj Dhodapkar
Portfolio: rutujdhodapkar(https://rutujdhodapkar.vercel.app)  
Contact: rutujdhodapkar@gmail.com   
- GitHub: rutujdhodapkar(https://github.com/rutujdhodapkar)

 Om Shelke
Contact: omdevdattshelke@gmail.com 
- GitHub: omshelke(https://github.com/OMShelke16)

 Anurag Vaishnav
Contact: av7ism@gmail.com

 Vishal Patil
Contact: vishalrpatil308@gmail.com
- GitHub: vishalpatil(https://github.com/vishalpatil308)
----

