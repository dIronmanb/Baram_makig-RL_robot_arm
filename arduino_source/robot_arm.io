const char tx = 1;  //assign tx with pin 1 (transmit)

//Setup
void setup()
{
  Serial.begin(9600);  //initialize serial communication for UART with baudrate 9.6kbps
  pinMode(tx, OUTPUT);  //set tx (or pin 1) as output
  on_off_motor(0,1);  //activate all servo motor channels on SC08A
}

//Main loop
void loop()  
{
    int a0 = analogRead(A0);
    int a1 = analogRead(A1);
    int a2 = analogRead(A2);



  /*
  Serial.print('\t');
  Serial.print(a0);
  Serial.print('\t');
  Serial.print(a1);
  Serial.print('\t');
  Serial.print(a2);
  Serial.println();

  */
 
    a0 = map(a0, 0, 1023, 0, 8191);
    a1 = map(a1, 0, 1023, 0, 8191);
    a2 = map(a2, 0, 1023, 0, 8191);



    set_ch_pos_spd(1, a0, 50);  //set position = 7300, speed = 50
    set_ch_pos_spd(2, a1, 50);
    set_ch_pos_spd(3, a2, 50);
 
  delay(100); //delay for a while *(delay have to set longer for lower, because the servo motor require more time to reach its position)
}

void on_off_motor(unsigned char channel, unsigned char on)
{
 
   unsigned char first_byte = 0;
   first_byte = 0b11000000 | channel; //make up 1st byte
   Serial.write(first_byte); //send 1st byte
   Serial.write(on); //send 2nd byte
}

void set_ch_pos_spd(unsigned char channel, unsigned int position, unsigned char velocity)
{

   unsigned char first_byte = 0;
   unsigned char high_byte = 0;
   unsigned char low_byte = 0;
   first_byte = 0b11100000 | channel; //make up the 1st byte
   high_byte = (position >> 6) & 0b01111111; //obtain the high byte of 13 bits position value
   low_byte = position & 0b00111111; //obtain the low byte of 13 bits position value
   Serial.write(first_byte); //send the 1st byte
   Serial.write(high_byte); //send the 2nd byte
   Serial.write(low_byte); //send the 3rd byte
   Serial.write(velocity); // send the 4th byte
}

void initial_position(unsigned char channel, unsigned int position) //optional, if used, the RX pin of Arduino Mainboard should be connected to TX pin of SC08A  
{

  unsigned char first_byte = 0;
  unsigned char high_byte = 0;
  unsigned char low_byte = 0;
  first_byte = 0b10000000 | channel; //make up the 1st byte
  high_byte = (position >> 6) & 0b01111111; //make up the high byte
  low_byte = position & 0b00111111; //make up the low byte
  Serial.write(first_byte); //send the 1st byte
  Serial.write(high_byte); //send the 2nd byte
  Serial.write(low_byte); //send the 3rd byte
  delay(100); //short delay for sending the data
  while(!Serial.available()); //wait untill data received
  while(Serial.read() != 0x04); //wait untill value 0x40 is received for indication
} 