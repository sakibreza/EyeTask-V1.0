package sample;

import javafx.application.Platform;
import javafx.fxml.FXMLLoader;

//This classes method will be called from python console
//This class is for py4j server connection
//This class will call methods in GuiController

public class EntryPoint {

    private GuiController guiController;
    private int value,timeGap = 10;

    //Entry point for py4j server
    public EntryPoint(FXMLLoader fxmlLoader){

        guiController = fxmlLoader.getController();

    }

    //---------------------------------------------

    //Command interface for executing function
    public interface Command{
        int execute();
    }


    //Wait for thread to complete
    public void Wait(){
        try {
            Thread.sleep(timeGap);
        }
        catch(Exception e){

        }
    }

    //Platform.runLater wrapper
    private int Wrap(final Command func)
    {
        Platform.runLater(new Runnable() {
            @Override
            public void run() {
                value = func.execute();
            }
        });

        Wait();
        return value;

    }


    //-------------------------------------------------

//----------------Initialization-------------

    //Initialization of gui elements
    public int init(int Speed,int Max_Speed,int Min_Speed,int Threshold,int Max_Thres,int Min_thres)
    {
        Command cd = new Command() { public int execute() {return guiController.init(Speed,Max_Speed,Min_Speed,Threshold,Max_Thres,Min_thres);} };
        return Wrap(cd);
    }

//----------------Focusing-------------


    //move focused button forward or backward
    public int moveFocus(int direction){

        Command cd = new Command() { public int execute() {return guiController.moveFocus(direction);} };
        return Wrap(cd);
    }

//----------------Wheelchair-------------

    //Increase speed of wheelchair
    public int increaseSpeed(){

        Command cd = new Command() { public int execute() {return guiController.increaseSpeed();} };
        return Wrap(cd);

    }

    //Decrease speed of wheelchair
    public int decreaseSpeed(){

        Command cd = new Command() { public int execute() {return guiController.decreaseSpeed();} };
        return Wrap(cd);
    }

//----------------Eye Threshold-------------

    //Decrease Threshold value of eye
    public int decreaseThres(){

        Command cd = new Command() { public int execute() {return guiController.decreaseThres();} };
        return Wrap(cd);
    }

    //Increase Threshold value of eye
    public int increaseThres(){

        Command cd = new Command() { public int execute() {return guiController.increaseThres();} };
        return Wrap(cd);
    }

//----------------Media-------------


    public int selectMedia(){
        Command cd = new Command() { public int execute() {return guiController.selectMedia();} };
        return Wrap(cd);
    }
    public int go(int Direction)
    {
        Command cd = new Command() { public int execute() {return guiController.go(Direction);} };
        return Wrap(cd);
    }
    public void playMedia(){

    }

    public void pauseMedia() {

    }

    public void stopMedia(){

    }


}
