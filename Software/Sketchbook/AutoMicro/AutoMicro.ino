// Simple Arduino G-Code controller for the stepper

int real_pos = 0;
int target_pos = 0;




// Pin defs
#define APG1 30
#define APP2 40
#define APP1 50

#define ANG1 31
#define ANP2 41
#define ANP1 51

#define BPG1 32
#define BPP2 42
#define BPP1 52

#define BNG1 33
#define BNP2 43
#define BNP1 53

void setup(){
	Serial.begin(115200);

	// Pin Initializations

	pinMode(APP1, OUTPUT);
	pinMode(APP2, OUTPUT);
	pinMode(APG1, OUTPUT);

	pinMode(ANP1, OUTPUT);
	pinMode(ANP2, OUTPUT);
	pinMode(ANG1, OUTPUT);

	pinMode(BPP1, OUTPUT);
	pinMode(BPP2, OUTPUT);
	pinMode(BPG1, OUTPUT);

	pinMode(BNP1, OUTPUT);
	pinMode(BNP2, OUTPUT);
	pinMode(BNG1, OUTPUT);

}

void loop(){
	// First, check for serial communication

	while (Serial.available()){
		char Axis = Serial.read(); // Currently discarded
		// Check for valid axis
		target_pos = Serial.parseInt();
		Serial.readStringUntil(" ");
	}
	if (real_pos != target_pos){
		update_stepper();
	}

}


void update_stepper(){

	Serial.println("Stepper Moving;");

	int direction = 1 - 2*(real_pos > target_pos);

	int ACoil;
	int BCoil;

	while (real_pos != target_pos){

		real_pos += direction;

		ACoil = round(sin(real_pos*HALF_PI));
		BCoil = round(cos(real_pos*HALF_PI));
		Serial.print(ACoil);Serial.print(",");Serial.println(BCoil);

		digitalWrite(APP1, ACoil == 1);
		digitalWrite(APP2, ACoil == 1);
		digitalWrite(APG1, ACoil == 1);

		digitalWrite(ANP1, ACoil == -1);
		digitalWrite(ANP2, ACoil == -1);
		digitalWrite(ANG1, ACoil == -1);

		digitalWrite(BPP1, BCoil == 1);
		digitalWrite(BPP2, BCoil == 1);
		digitalWrite(BPG1, BCoil == 1);

		digitalWrite(BNP1, BCoil == -1);
		digitalWrite(BNP2, BCoil == -1);
		digitalWrite(BNG1, BCoil == -1);
		delay(50);

	}

	Serial.println("Done");
}