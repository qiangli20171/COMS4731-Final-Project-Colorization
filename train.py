from models import *
from dataset import *
from utils import *
import torchvision
import torch
import torch.optim as optim
import torch.utils.data as data
import torch.nn as nn

if __name__ == '__main__':

    color_net = complete_net()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)
    color_net.to(device)
    color_net.cuda()
    criterion = nn.MSELoss()
    optimizer = optim.RMSprop(color_net.parameters(), lr=1e-6, momentum=0.9)
    # optimizer = optim.Adam(color_net.parameters(), lr=1e-3)

    transform = torchvision.transforms.Compose(
        [torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    # changes:
    # didn't use the transform
    # place_dataset = PlaceDataset(image_dir = 'places_train/', transform=transform)
    place_dataset = PlaceDataset(image_dir = 'train_church/')
    dataset_len = len(place_dataset)
    train_size = int(0.1*dataset_len)
    print(train_size)
    val_size = int(dataset_len-train_size)
    train_dataset, val_dataset = data.random_split(place_dataset, [train_size, val_size])
    train_loader = data.DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=16)
    val_loader = data.DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=16)
    train_loader_size = len(train_loader)
    print(train_loader_size)
    total_loss_list = []
    
    with open("loss.csv", "w") as f:
        f.write("epoch,loss\n")

    for epoch in range(1):
      
        running_loss = 0.0
        val_loss = 0.0
        loss_display_step = 5
        total_loss = 0.0

        for i, data in enumerate(train_loader, 0):

            inputs, embeds, labels = data['image'], data['embedding'], data['label']
            inputs, embeds, labels = inputs.to(device), embeds.to(device), labels.to(device)
          
            optimizer.zero_grad()

            outputs = color_net(inputs.float(), embeds.float())

            loss = criterion(outputs, labels.float())
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            total_loss += loss.item()

            if i % loss_display_step == loss_display_step-1:
                # make running_loss larger to see the small changes...
                running_loss = running_loss * 1e5
                print('[%d, %5d] training loss: %.3f validation accurancy: %.3f'
                % (epoch + 1, i + 1, running_loss / loss_display_step, val_loss / loss_display_step))
                running_loss = 0.0
                val_loss = 0.0

        if (epoch+1)%1 == 0:
            torch.save(color_net.state_dict(), 'colornet_v1_%d.pth'%(epoch+1))
            total_loss = total_loss * 1e5
            epoch_loss = total_loss / train_loader_size
            total_loss = 0.0
            with open("loss.csv", "w") as f:
                f.write(",".join([str(epoch), str(epoch_loss)]))
                f.write("\n")

    print('Finished Training')
