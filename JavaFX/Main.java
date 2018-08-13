package JavaFX;

import py4j.GatewayServer;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class Main extends Application {

    @Override
    public void start(Stage primaryStage) throws Exception{
        FXMLLoader loader = new FXMLLoader(getClass().getResource("Gui.fxml"));
        Parent root = (Parent) loader.load();
        primaryStage.setTitle("Eye Gaze");
        primaryStage.setScene(new Scene(root, 259, 384));
        primaryStage.show();
        GatewayServer gatewayServer = new GatewayServer(new EntryPoint(loader));
        gatewayServer.start();

    }

    public static void main(String[] args) {
        launch(args);
    }
}
