require('dotenv').config();                                     // dotenv file module
const csv = require('csv-parser');                              // csv file parser module
const fs = require('fs');                                       // file system module
const Insta = require('scraper-instagram');                     // Instagram scraper module
const InstaClient = new Insta();                                // Instagram module instance

let csvFileText = "Name,Website,Instagram_Username,Instagram_Followers,Instagram_Following,Instagram_Total_Posts\n"

/**
 * Instagram Scraper Function for scrap data from instagram
 * @param {String} username
 * @param {Number} indexNumber
 */
 async function instagramScraper (username, indexNumber) {
    let identifier = result[indexNumber];
    await InstaClient.getProfile(username)
        .then(profile => {
            let followersCount = profile.followers;
            let followingCount = profile.following;
            let totalPostsCount = profile.posts;
            identifier.Instagram_Followers_Count = followersCount;
            identifier.Instagram_Following_Count = followingCount;
            identifier.Instagram_Total_Posts_Count = totalPostsCount;
        })
        .catch(error => {
            if (error) {
                identifier.Instagram_Followers_Count = "Not Found";
                identifier.Instagram_Following_Count = "Not Found";
                identifier.Instagram_Total_Posts_Count = "Not Found";
            }
        })
        .finally(() => {
            let newData = `${identifier.Name},${identifier.Web},${identifier.Instagram_User},${identifier.Instagram_Followers_Count},${identifier.Instagram_Following_Count},${identifier.Instagram_Total_Posts_Count}\n`;
            csvFileText = csvFileText.concat(newData);
            console.log(`${indexNumber} is passed...`);
        })
}


const result = [];

fs.createReadStream(process.env.CSV_FILE_PATH)
    .pipe(csv())
    .on("data", (data) => {
        result.push(data);
    })
    .on("end", () => {
        InstaClient.authBySessionId(process.env.INSTAGRAM_SESSION_ID)
            .then((account) => {
                if (account) {
                    for (let item = 0; item < result.length; item++) {
                        let instagramUserName = result[item].Instagram_User;
                        instagramScraper(instagramUserName, item)
                            .finally(() => {
                                if (item == result.length - 1) {
                                    fs.writeFile("./instagram_output_data.csv", csvFileText, error => {
                                        if (error) {
                                            console.log(error);
                                        } else {
                                            console.log("File Written successful.... :)");
                                        }
                                    });
                                }
                            });
                    }
                }
            })
            .catch(error => {
                console.log(error);
            });
    });

