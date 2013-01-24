exports.lower = function (input)
{
    return input.toString().toLowerCase();
};

exports.truncate = function (input, length)
{
    var smallString = input.toString().substring(0, length);
  
    if (smallString.length != input.toString().length)
        smallString += "...";
    
    return smallString;
};