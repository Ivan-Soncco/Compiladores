public class MyClass extends BaseClass {
    public static void main(String[] args) {
        try {
            System.out.println("Hello");
        } finally {
            super.cleanup();
        }
    }
}