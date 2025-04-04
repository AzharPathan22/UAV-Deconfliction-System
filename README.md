# UAV Strategic Deconfliction System

This project implements a strategic deconfliction system for UAV missions. It checks for spatial and temporal conflicts between a primary drone mission and several simulated flight schedules. The system is built in Python and uses libraries such as Matplotlib for visualization and basic logging for debugging.

## Features
- **Primary Mission Input:**  
  Enter the primary drone mission details (drone ID, waypoints with coordinates and timestamps) interactively.
- **Simulated Flight Schedules:**  
  Hardcoded simulated missions for multiple drones.
- **Conflict Detection:**  
  Checks for spatial conflicts by interpolating positions over overlapping time intervals.
- **Visualization:**  
  Plots the flight paths of the missions and highlights conflict points.
- **Testing:**  
  Basic tests are included to validate distance calculations and interpolation logic.

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/AzharPathan22/UAV-Deconfliction-System.git
   cd UAV-Deconfliction-System

2. **Create and Activate a Virtual Environment (Optional but Recommended):**

    ```bash
    python -m venv flytbase_env
    # Activate the environment:
    # On Windows:
    flytbase_env\Scripts\activate
    # On macOS/Linux:
    source flytbase_env/bin/activate

3. **Install Dependencies: Install the required Python libraries using pip:**

    ```bash
    pip install matplotlib


## Execution

1. **Run the main script using:**

    ```bash
    python deconfliction_system.py

2. **The script will:**

    Run basic tests to validate utility functions.

    Prompt you to enter the primary drone mission details.

    Use hardcoded simulated flight schedules.

    Detect any conflicts and print them to the console.

    Display a 2D plot of the flight paths with conflicts highlighted.

3. **File Structure**
    
    deconfliction_system.py: Main script containing the implementation.

    README.md: This file.

    Additional documentation (Reflection & Justification) is provided in Reflection_and_Justification.md.
