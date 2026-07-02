#!/bin/bash
python main.py &
streamlit run src/dashboard.py --server.port $PORT --server.address 0.0.0.0
