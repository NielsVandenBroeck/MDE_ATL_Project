# MDE_ATL_Project
Final project for the course Model Driven Engineering

# Rule-Based Translational Semantics: RPG to Petri Net
This project explores the application of Model Driven Engineering (MDE) and ATLAS Transformation Language (ATL) to translate the static rules of a Role-Playing Game (RPG) into a dynamic, executable Petri Net. The resulting model allows for the simulation of game mechanics such as movement, inventory management, and trap detection.

Requires Eclipse IDE with EMF and ATL plugins installed.
Advised to Visualize and simulate resulting Petri Nets in TAPAAL.

# Usage Workflow
1. Metamodeling & Instantiation
Ensure RPG.ecore and PetriNet.ecore are registered in your Eclipse environment. The ExampleRPG.xmi file serves as the input model, featuring a hero named "Warrior" with 10 lives starting in the "Forest" level.

2. ATL Transformation
Run the RPG2PetriNet.atl transformation configuration in Eclipse:

Source (IN): ExampleRPG.xmi

Target (OUT): TransformedPetriNet.xmi

This process generates the structural mapping of the Petri Net, including places for tiles and transitions for valid movements.

3. Visualization Conversion
The raw XMI output is not directly viewable. Run the included Python script to generate a .tapn file:

```Bash
python xmi2tapn.py
```

Note: The script expects the input file to be named TransformedPetriNet.xmi and outputs TransformedPetriNet.tapn.

4. Simulation
Open TransformedPetriNet.tapn in TAPAAL. You can now simulate the game logic using Petri Net tokens.
