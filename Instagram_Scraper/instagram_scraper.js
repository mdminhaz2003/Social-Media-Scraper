require('dotenv').config();                                     // dotenv file module
const csv = require('csv-parser');                              // csv file parser module
const fs = require('fs');                                       // file system module
const Insta = require('scraper-instagram');                     // Instagram scraper module
const InstaClient = new Insta();                                // Instagram module instance

let csvFileHeaders = "Name,Website,Instagram_Username,Instagram_Followers,Instagram_Following,Instagram_Total_Posts\n"
fs.appendFile('./instagram_output_data.csv', csvFileHeaders, (error) => {
    console.log(error);
});
const result = [];

fs.createReadStream(process.env.CSV_FILE_PATH)
    .pipe(csv())
    .on("data", (data) => {
        result.push(data);
    })
    .on("end", () => {
        InstaClient.authBySessionId(process.env.INSTAGRAM_SESSION_ID)
            .then(() => {
                for (let item = 0; item < result.length; item++) {
                    let instagramUserName = result[item].Instagram_User;
                    let identifier = result[item];
                    if (instagramUserName != "") {
                        InstaClient.getProfile(instagramUserName)
                        .then((profile) => {
                            let followersCount = profile.followers;
                            let followingCount = profile.following;
                            let totalPostsCount = profile.posts;
                            identifier.Instagram_Followers_Count = followersCount;
                            identifier.Instagram_Following_Count = followingCount;
                            identifier.Instagram_Total_Posts_Count = totalPostsCount;
                        })
                        .catch((error) => {
                            if (error) {
                                identifier.Instagram_Followers_Count = "Not Found";
                                identifier.Instagram_Following_Count = "Not Found";
                                identifier.Instagram_Total_Posts_Count = "Not Found";
                            }
                        })
                        .finally(() => {
                            let newData = `${identifier.Name},${identifier.Web},${identifier.Instagram_User},${identifier.Instagram_Followers_Count},${identifier.Instagram_Following_Count},${identifier.Instagram_Total_Posts_Count}\n`;
                            console.log(newData);
                            fs.appendFile('./instagram_output_data.csv', newData, (err) => {
                                if (err) throw err;
                                console.log('New Data was appended to file!');
                            });
                        });
                    } else {
                        console.log("Empty Cell !!!");
                        continue;
                    }

                }
            })
            .catch((error) => {
                console.log(error);
            });
    });