
#include <LCDWIKI_GUI.h> //Core graphics library
#include <LCDWIKI_KBV.h> //Hardware-specific library

//if the IC model is known or the modules is unreadable,you can use this constructed function
LCDWIKI_KBV mylcd(ILI9486,A3,A2,A1,A0,A4); //model,cs,cd,wr,rd,reset
//if the IC model is not known and the modules is readable,you can use this constructed function
//LCDWIKI_KBV mylcd(320,480,A3,A2,A1,A0,A4);//width,height,cs,cd,wr,rd,reset

//define some colour values
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

int i=60;
int height = mylcd.Get_Height();
int width  = mylcd.Get_Width();
String read_String;

void setup() 
{
  Serial.begin(115200);
  mylcd.Init_LCD();
  //Serial.println(mylcd.Read_ID(), DEC);
  mylcd.Fill_Screen(BLACK);
  mylcd.Set_Text_colour(RED);
  mylcd.Set_Text_Back_colour(BLACK);
  mylcd.Set_Text_Size(2);
  mylcd.Print_String(String(mylcd.Read_ID()), 0, 0);
  mylcd.Print_Number_Int(height, 0, 20, 0, ' ', 10);
  mylcd.Print_Number_Int(width, 0, 40, 0, ' ', 10);   
}

void loop() 
{  
  if (Serial.available() > 0) {        
    //mylcd.Vert_Scroll(0, 100, 400);
      mylcd.Print_String(Serial.readStringUntil(';'), 0, i);
      i += 20;
      //delay(1000);
  }
  /*String incomingByte;
    if (Serial.available() > 0){
        incomingByte = Serial.readStringUntil('\n'); // read byte
        //read_String += incomingByte;
    }

    if(read_String != ""){
        mylcd.Print_String(incomingByte, 0, i);
        i += 20;
    }
    incomingByte = "";
   */ 
}
