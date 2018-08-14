package sample;

import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.MenuButton;
import javafx.scene.control.MenuItem;

public class GuiController {

    @FXML
    private Button speedIncrease,speedDecrease,thresIncrease,thresDecrease,buttonPlay,buttonPause,buttonStop; //Instances of buttons

    @FXML
    private MenuButton buttonMedia;
    @FXML
    private MenuItem item1,item2;

    private Button[] guiButtons; //Array of buttons

    @FXML
    private Label speedValue,thresValue; //Label Parameters

    private int Speed,Threshold,no_of_buttons = 8;//Value of Label Parameters

    private int Max_Speed,Min_Speed,Max_Thres,Min_Thres;//Minimum and Maximum values of parameters

    private int buttonFocused = 0;//Current focused button

    //----------------Initialization-------------

    //Initialization of gui elements
    public int init(int Speed,int Max_Speed,int Min_Speed,int Threshold,int Max_Thres,int Min_thres)
    {
        //Buttons Initialization
        guiButtons = new Button[no_of_buttons];
        guiButtons[0] = speedIncrease;
        guiButtons[1] = speedDecrease;
        guiButtons[2] = thresIncrease;
        guiButtons[3] = thresDecrease;
        guiButtons[5] = buttonPlay;
        guiButtons[6] = buttonPause;
        guiButtons[7] = buttonStop;

        //Set parameters value
        this.Speed = Speed;
        this.Max_Speed = Max_Speed;
        this.Min_Speed = Min_Speed;
        speedValue.setText(Speed+"");

        this.Threshold = Threshold;
        this.Max_Thres = Max_Thres;
        this.Min_Thres = Min_thres;
        thresValue.setText(Threshold+"");

        //Set focus on the current button
        guiButtons[buttonFocused].requestFocus();

        return 1;//If initialization ok then return 1


    }

    //----------------Focusing Button-------------

    //move button focus forward or backward
    @FXML
    public int moveFocus(int direction)
    {

        if (direction == 1) //if direction 1 then go forward
        {
            if(buttonFocused == no_of_buttons - 1)
                buttonFocused = 0;
            else
                buttonFocused = buttonFocused + 1;
        }
        else if(direction == -1)//else go backward
        {
            if(buttonFocused == 0)
                buttonFocused = no_of_buttons - 1;
            else
                buttonFocused = buttonFocused - 1;
        }

        //set focus on the current button
        guiButtons[buttonFocused].requestFocus();

        return buttonFocused;//return the currently focused button_no

    }

    //----------------Wheel Chair-------------

    //Increase speed of wheelchair
    @FXML
    public int increaseSpeed() {

        Speed = (Speed + 1 > Max_Speed)?Speed:Speed+1;
        speedValue.setText(Speed+"");
        return Speed;//return speed of wheelchair

    }

    //Decrease speed of wheelchair
    @FXML
    public int decreaseSpeed() {

        Speed = (Speed - 1 < Min_Speed)?Speed:Speed-1;
        speedValue.setText(Speed+"");
        return Speed;//return speed of wheelchair
    }

    //----------------Eye Threshold-------------

    //Decrease Threshold value of eye
    @FXML
    public int decreaseThres() {

        Threshold = (Threshold - 1 < Min_Thres)?Threshold:Threshold-1;
        thresValue.setText(Threshold+"");
        return  Threshold;//return Threshold value of eye

    }

    //Increase Threshold value of eye
    @FXML
    public int increaseThres() {

        Threshold = (Threshold + 1 > Max_Thres)?Threshold:Threshold+1;
        thresValue.setText(Threshold+"");
        return  Threshold;//return Threshold value of eye

    }

    //----------------Media-------------

    @FXML
    public int selectMedia(){
        buttonMedia.fire();
        item1.setStyle("-fx-background-color:#c3d0e5");
        return 0;
    }

    public int go(int Direction)
    {
        item1.setStyle("-fx-background-color:white");
        item2.setStyle("-fx-background-color:#c3d0e5");
        return 0;
    }

    @FXML
    public void playMedia(){

    }

    @FXML
    public void pauseMedia() {

    }

    @FXML
    public void stopMedia(){

    }

}
