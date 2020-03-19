#modloaded ordinarycoins
// Allows coins to be exchanged at an 8:1 ratio for the next tier, or vice versa.

import crafttweaker.item.IItemStack;
import crafttweaker.item.IIngredient;

val coinTypes = [<ordinarycoins:coinbronze>, <ordinarycoins:coinsilver>, <ordinarycoins:coingold>, <ordinarycoins:coinplatinum>] as IItemStack[];
for i in 0 to 3 {
    addCoinConversionRecipes(coinTypes[i], coinTypes[i+1]);
}

function addCoinConversionRecipes(smaller as IItemStack, greater as IItemStack) {
    val smallerName = smaller.name.replace("item.ordinarycoins.", "") as string;
    val greaterName = greater.name.replace("item.ordinarycoins.", "") as string;
    
    // Create stacking recipe
    val stackRecipeName = smallerName + "To" + greaterName[0].toUpperCase() + greaterName.substring(1) as string;
    recipes.addShapeless(stackRecipeName, greater, [smaller, smaller, smaller, smaller, smaller, smaller, smaller, smaller]);
    
    // Create unstacking recipe
    val unstackRecipeName = greaterName + "To" + smallerName[0].toUpperCase() + smallerName.substring(1) as string;
    recipes.addShapeless(unstackRecipeName, smaller * 8, [greater]);
}