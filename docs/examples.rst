.. _examples_section:

Examples
========

Welcome to the examples section for metaprivBIDS. Below is an interactive tutorial going through all the steps of how to run the metaprivBIDS GUI. 

Interactive Tutorial
--------------------

This is an interactive step-by-step guide:

.. raw:: html

    <div style="max-width: 600px; margin: 0 auto;">
        <img id="tutorialImage" src="_static/image1.png" style="width: 100%; border: 2px solid #000;">
        <br>
        <button onclick="previousImage()" style="margin-top: 10px;">Previous</button>
        <button onclick="nextImage()" style="margin-top: 10px;">Next</button>
        <br>
        <p id="imageText" style="margin-top: 10px;">Step 1: This is the first step of the tutorial.</p>
    </div>

    <script type="text/javascript">
        var images = [
            "_static/img1.png",
            "_static/img2.png",
            "_static/img3.png",
            "_static/img4.png",
            "_static/img5.png",
            "_static/img6.png",
            "_static/img7.png",
            "_static/img8.png",
            "_static/img9.png",
            "_static/img10.png",
            "_static/img11.png",
            "_static/img12.png",
            "_static/img13.png",
            "_static/img14.png",

        ];
        var texts = [
            "Step 1: The Load button prompts the user with the option to load in the dataset for analysis.",

            "Step 2: After loading the dataset, the user can then manually select columns (quasi-identifiers) by clicking on the field in the Select Column (highlighting them in blue).<br>" + 
            "<p style='margin-top: 16px;'> The field 'Unique Value' indicates how many unique values can be found in the column. The 'Type' field shows whether or not a column is continuous or categorical, " +
            "and the 'Sensitive Attribute' field is an optional column for the user to select a sensitive attribute." + 
            
            "<p style='margin-top: 16px;'> Sensitive attributes typically include information that could lead to discrimination, stigma, or other forms of harm if disclosed, such as medical conditions, sexual orientation," +
            " religious beliefs, or financial status. Hence for our example, Disease is set as a sensitive attribute." + 
            
            "<p style='margin-top: 16px;'> We have excluded 'exercise_weekly_hours' from our analysis because quasi-identifiers are required to possess a temporally static characteristic.",

            "Step 3: The Privacy Calculation button returns the user metrics for the chosen quasi-identifiers, including the number of unique rows, k-Anonymity & L-Diversity.<br>" +
            "From the data example we see that K = 1, L = 1, and the number of unique rows is 190 out of the total row count of 200, indicating a high privacy risk.",

            "Step 4: To get an overview of the individual columns' contribution to the dataset, we can push the Variable Optimization button.<br>" +
            "<p style='margin-top: 16px;'>Here the Quasi Identifier field indicates all the chosen columns. " +
            "The Difference field shows the difference between the total amount of unique rows for all combined columns and the total amount of unique rows if the given quasi-identifier were to be removed. " +
            "The Normalized field captures the importance a quasi-identifier has on the overall unique rows given its unique value count." +

            "<p style='margin-top: 16px;'>That means that columns with a low number of unique values are expected to overall not have a high impact on unique rows. " +
            "E.g., from the example dataset, we see that 'Sex' has a normalized score of 1.0, whereas 'marital-status' has a score of 0.3. Both identifiers contribute, " + 
            "in absolute numbers, the same amount to the unique rows, but 'Sex' scores higher because it is normalized by the unique values.",

            "Step 5: The Compute Suda button is based on the Special Uniques Detection Algorithm (SUDA). SUDA takes a two-step approach." +
            "<p style='margin-top: 16px;'>In the first step, all unique attribute sets (up to a user-specified size) are located at the record level. " +
            "Once all MSUs have been found, a SUDA score is assigned to each record indicating how 'risky' it is, using the size and distribution of MSUs within each record." +
            "<p style='margin-top: 16px;'>The potential risk of the records is assessed based on two factors:" +
            "<p style='margin-top: 16px;'>1) the smaller the size of the MSU within a record, the higher the risk associated with that record.<br>" + 
            "2) the greater the number of MSUs contained in the record, the higher its risk." +

            "<p style='margin-top: 16px;'> The user will be asked to specify the maximum size of variables to consider. This can be a minimum of 1 field and a maximum of the total number of available fields.<br>" +
            " The Data Intrusion Simulation (DIS) metric has to be between 0 and 1; the default is set to 0.2. The higher the DIS, the more background knowledge we assume an adversary has.",

            "Step 6: To see a preview of the data the user can push the Preview Data Button.",

            "Step 7: The Preview Data button takes the user to a new page with different options for data anonymization, e.g., round values, combine categorical values, etc.",

            "Step 8: The Combine Categorical button provides the user with an option to generalise categorical values.<br>" + 
            "<p style='margin-top: 16px;'> We can for example see from our test data that it would make sense to combine all educational steps below high school into one category called 'K-12 education'." ,

            "Step 9: To keep track of changed categorical values, the user has the option to push the Graph Categorical button, which keeps track of changes for categorical values.",

            "Step 10: Returning back to the Main Menu we can push the Privacy Information Factor button.",

            "Step 11: This takes the user to a new page where the Cell Information Gain (CIG) can be computed." +
            " Importantly, the user has the option to specify if there are any missing values in the form of (NaN) values or other entries indicating missing values. In this case, the computation of CIG will automatically set these to 0, ensuring that they do not count toward a privacy risk.",

            "Step 12: This will then prompt the CIG value for all individual cell values. To get the privacy risk for the row, the RIG is computed and displayed in the outermost right field." +
            " For the dataset we see that rows with index 169, 167, 37, 52 & 159 are the top 5 rows with the highest risk." +
            " Additionally we see that PIF is 21.38, higher than the recommended guidelines seen below." +

            

            "<p style='margin-top: 16px;'>  Example thresholds for different Data Safe levels <a href='https://www.infogovanz.com/wp-content/uploads/2020/01/191202-ACS-Privacy-eReport.pdf'>[ACS Privacy Impact Assessment eReport]</a>:<br>" +

            " Safe Level 1: 1.00 ≤ PIF <br>" +
            " Safe Level 2: 0.33 ≤ PIF < 1.00 <br>" +
            " Safe Level 3: 0.11 ≤ PIF < 0.33 <br>" +
            " Safe Level 4: 0.04 ≤ PIF < 0.11 <br>" +
            " Safe Level 5: PIF < 0.04 <br>" +
            
            "<p style='margin-top: 16px;'> The user can, based on this information, choose to anonymise the data further by using the methods from the preview page or, manually outside the program, discard rows with a user-specified threshold",


            "Step 13: To access the data privacy risk on a field level we can use the Generate CIG Heatmap button.<br>" +
            " This gives the user the opportunity to directly view which quasi-identifiers contribute the most to the overall risk in the dataset." +
            
            "<p style='margin-top: 16px;'> For example, here we see that Age has a very high contribution to the risk factor whereas Sex and Salary-class contribute less.",

            "Step 14: After having performed some of the anonymising techniques from the preview page, we see a big improvement to our overall Privacy Information Factor." +
            "<p style='margin-top: 16px;'> The user is advised to keep track of the trade-off between utility and privacy; there is no one-size-fits-all solution regarding which anonymisation techniques to use, but rather suggestions for improving the available privacy risk measures from the metaprivBIDS platform." ,
            



    
        ];

        var currentIndex = 0;

        function showImage(index) {
            var imageElement = document.getElementById("tutorialImage");
            var textElement = document.getElementById("imageText");
            imageElement.src = images[index];
            textElement.innerHTML = texts[index];
            MathJax.typeset(); // Ensure MathJax processes the newly inserted content
        }

        function nextImage() {
            currentIndex++;
            if (currentIndex >= images.length) {
                currentIndex = 0;
            }
            showImage(currentIndex);
        }

        function previousImage() {
            currentIndex--;
            if (currentIndex < 0) {
                currentIndex = images.length - 1;
            }
            showImage(currentIndex);
        }
    </script>

